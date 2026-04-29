#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

from src.core.exceptions import ZaomengError
from src.modules.distillation_second_pass import (
    build_second_pass_messages,
    parse_markdown_kv,
    render_overlap_report,
    render_peer_profile_contrasts,
)


class DistillationRefinementMixin:
    def _refine_profile_with_llm(
        self,
        profile: Dict[str, Any],
        *,
        bucket: Dict[str, List[str]],
        arc_values: List[Tuple[int, Dict[str, int]]],
        peer_profiles: Optional[Dict[str, Dict[str, Any]]] = None,
        overlap_report: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        local_refined = dict(profile)
        if not self._should_use_llm_second_pass():
            return local_refined

        try:
            character_hint = self._resolve_character_hint(str(local_refined.get("name", "")))
            messages = self._build_second_pass_messages(
                local_refined,
                bucket,
                arc_values,
                peer_profiles=peer_profiles or {},
                overlap_report=overlap_report or [],
                character_hint=character_hint,
            )
            messages[0]["content"] = (
                f"{messages[0]['content']}\n\n"
                "宸垎淇瑕佹眰:\n"
                "- 蹇呴』鍒╃敤鍚岀粍鍏朵粬瑙掕壊鐨勫姣旀憳瑕侊紝鎷夊紑褰撳墠瑙掕壊涓庝粬浠殑鍖哄埆銆俓n"
                "- 濡傛灉褰撳墠鑽夌涓庡叾浠栬鑹插瓨鍦ㄩ珮搴﹂噸鍚堝瓧娈碉紝浼樺厛鏀瑰啓杩欎簺瀛楁銆俓n"
                "- 杈撳嚭鏃朵繚鐣欒瘉鎹敮鎸侊紝绂佹涓轰簡宸紓鑰岀‖缂栬瀹氥€?"
            )
            messages[1]["content"] = "\n\n".join(
                [
                    messages[1]["content"],
                    "## Character Hint",
                    self._render_character_hint(str(profile.get("name", "")), character_hint),
                    "## Peer Contrast",
                    self._render_peer_profile_contrasts(profile["name"], peer_profiles or {}),
                    "## Overlap Alerts",
                    self._render_overlap_report(overlap_report or []),
                ]
            )
            response = self.llm_client.chat_completion(
                messages,
                temperature=0.2,
                max_tokens=1600,
            )
            content = str(response.get("content", "")).strip()
            if not content:
                return local_refined
            parsed = self._parse_markdown_kv(content)
            if not parsed:
                return local_refined
            refined = self._apply_profile_refinement(local_refined, parsed)
            refined["arc_summary"] = self._infer_arc_summary(refined.get("arc", {}))
            refined["arc_confidence"] = self._safe_int(parsed.get("arc_confidence", refined.get("arc_confidence", 0)))
            return refined
        except ZaomengError as exc:
            self.logger.warning("Skipping LLM second pass for %s: %s", profile.get("name", "unknown"), exc)
            return local_refined

    def _should_use_llm_second_pass(self) -> bool:
        if self.second_pass_mode == "rule-only":
            return False
        if self.second_pass_mode == "llm-only":
            return True
        return bool(getattr(self.llm_client, "is_generation_enabled", lambda: False)())

    def _refine_profile_locally(
        self,
        profile: Dict[str, Any],
        *,
        bucket: Dict[str, List[str]],
        peer_profiles: Dict[str, Dict[str, Any]],
        overlap_report: List[str],
    ) -> Dict[str, Any]:
        return dict(profile)

    def _build_second_pass_messages(
        self,
        profile: Dict[str, Any],
        bucket: Dict[str, List[str]],
        arc_values: List[Tuple[int, Dict[str, int]]],
        *,
        peer_profiles: Optional[Dict[str, Dict[str, Any]]] = None,
        overlap_report: Optional[List[str]] = None,
        character_hint: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        prompt_text = self._load_auxiliary_markdown(
            "prompt_file",
            "distill_prompt.md",
            fallback=(
                "# 浜虹墿妗ｆ钂搁\n"
                "浣犻渶瑕佸湪鐜版湁瑙勫垯鑽夌鍩虹涓婂仛绗簩娆℃彁鐐硷紝寮哄寲娣卞眰浜烘牸銆侀樁娈靛姬鍏変笌宸紓鍖栬〃杈俱€?"
            ),
        )
        schema_text = self._load_auxiliary_markdown("reference_file", "output_schema.md", fallback="# 杈撳嚭瑙勮寖")
        style_text = self._load_auxiliary_markdown("reference_file", "style_differ.md", fallback="# 椋庢牸宸紓鍖?")
        logic_text = self._load_auxiliary_markdown("reference_file", "logic_constraint.md", fallback="# 閫昏緫绾︽潫")
        draft_markdown = self._render_profile_md(profile)
        evidence_markdown = self._render_second_pass_evidence(profile["name"], bucket, arc_values)
        hint_markdown = self._render_character_hint(str(profile.get("name", "")), character_hint or {})
        draft_with_contrast = "\n\n".join(
            [
                draft_markdown,
                "## Peer Contrast",
                self._render_peer_profile_contrasts(profile["name"], peer_profiles or {}),
                "## Overlap Alerts",
                self._render_overlap_report(overlap_report or []),
            ]
        )
        return build_second_pass_messages(
            prompt_text=prompt_text,
            schema_text=schema_text,
            style_text=style_text,
            logic_text=logic_text,
            draft_markdown=draft_with_contrast,
            hint_markdown=hint_markdown,
            evidence_markdown=evidence_markdown,
        )

    def _render_second_pass_evidence(
        self,
        name: str,
        bucket: Dict[str, List[str]],
        arc_values: List[Tuple[int, Dict[str, int]]],
    ) -> str:
        timeline = list(bucket.get("timeline", []))
        stage_windows = self._build_stage_windows(timeline)
        lines = [
            f"# EVIDENCE FOR {name}",
            "",
            "## Early Stage",
        ]
        lines.extend(f"- {line}" for line in stage_windows.get("start", [])[: self.llm_evidence_lines_per_stage])
        lines.extend(["", "## Mid Stage"])
        lines.extend(f"- {line}" for line in stage_windows.get("mid", [])[: self.llm_evidence_lines_per_stage])
        lines.extend(["", "## Late Stage"])
        lines.extend(f"- {line}" for line in stage_windows.get("end", [])[: self.llm_evidence_lines_per_stage])
        lines.extend(["", "## Dialogue Samples"])
        lines.extend(f"- {line}" for line in self._dedupe_texts(bucket.get("dialogues", []), 8)[:8])
        lines.extend(["", "## Thought Samples"])
        lines.extend(f"- {line}" for line in self._dedupe_texts(bucket.get("thoughts", []), 6)[:6])
        lines.extend(["", "## Description Samples"])
        lines.extend(f"- {line}" for line in self._dedupe_texts(bucket.get("descriptions", []), 6)[:6])
        lines.extend(["", "## Arc Metrics"])
        for idx, values in arc_values[:12]:
            lines.append(f"- chunk_{idx}: {self._join_metric_map(values)}")
        return "\n".join(lines).rstrip() + "\n"

    def _render_peer_profile_contrasts(
        self,
        name: str,
        peer_profiles: Dict[str, Dict[str, Any]],
    ) -> str:
        return render_peer_profile_contrasts(
            name,
            peer_profiles,
            split_persona_scalar=self._split_persona_scalar,
        )

    @staticmethod
    def _render_overlap_report(overlap_report: List[str]) -> str:
        return render_overlap_report(overlap_report)

    def _load_auxiliary_markdown(self, method_name: str, filename: str, fallback: str) -> str:
        resolver = getattr(self.path_provider, method_name, None)
        if resolver is None:
            return fallback
        path = resolver(filename)
        if not path or not Path(path).exists():
            return fallback
        return Path(path).read_text(encoding="utf-8")

    @staticmethod
    def _parse_markdown_kv(text: str) -> Dict[str, str]:
        return parse_markdown_kv(text)

    def _apply_profile_refinement(self, profile: Dict[str, Any], parsed: Dict[str, str]) -> Dict[str, Any]:
        refined = dict(profile)
        list_fields = {
            "core_traits",
            "typical_lines",
            "decision_rules",
            "life_experience",
            "taboo_topics",
            "forbidden_behaviors",
            "strengths",
            "weaknesses",
            "cognitive_limits",
            "fear_triggers",
            "key_bonds",
            "signature_phrases",
            "sentence_openers",
            "connective_tokens",
            "sentence_endings",
            "forbidden_fillers",
        }
        dict_targets = {
            "cadence": ("speech_habits", "cadence"),
            "signature_phrases": ("speech_habits", "signature_phrases"),
            "sentence_openers": ("speech_habits", "sentence_openers"),
            "connective_tokens": ("speech_habits", "connective_tokens"),
            "sentence_endings": ("speech_habits", "sentence_endings"),
            "forbidden_fillers": ("speech_habits", "forbidden_fillers"),
            "anger_style": ("emotion_profile", "anger_style"),
            "joy_style": ("emotion_profile", "joy_style"),
            "grievance_style": ("emotion_profile", "grievance_style"),
        }
        direct_fields = {
            "speech_style",
            "identity_anchor",
            "soul_goal",
            "trauma_scar",
            "worldview",
            "thinking_style",
            "temperament_type",
            "core_identity",
            "faction_position",
            "background_imprint",
            "world_rule_fit",
            "social_mode",
            "hidden_desire",
            "inner_conflict",
            "story_role",
            "belief_anchor",
            "moral_bottom_line",
            "self_cognition",
            "stress_response",
            "others_impression",
            "restraint_threshold",
            "private_self",
            "stance_stability",
            "reward_logic",
            "action_style",
            "arc_summary",
        }

        for key, value in parsed.items():
            if key in {"arc_start", "arc_mid", "arc_end"}:
                bucket_name = key.split("_", 1)[1]
                arc_bucket = dict(refined.get("arc", {}).get(bucket_name, {}))
                arc_bucket.update(self._split_metric_map(value))
                refined.setdefault("arc", {})[bucket_name] = arc_bucket
                continue
            if key == "values":
                value_map = self._split_metric_map(value)
                if value_map:
                    refined["values"] = {
                        metric: max(0, min(10, self._safe_int(metric_value)))
                        for metric, metric_value in value_map.items()
                    }
                continue
            if key in dict_targets:
                parent, child = dict_targets[key]
                parent_bucket = dict(refined.get(parent, {})) if isinstance(refined.get(parent, {}), dict) else {}
                parent_bucket[child] = self._split_persona_scalar(value) if key in list_fields else value
                refined[parent] = parent_bucket
                continue
            if key in direct_fields:
                refined[key] = value
                continue
            if key in list_fields:
                refined[key] = self._split_persona_scalar(value)
        return refined

    @staticmethod
    def _split_persona_scalar(value: str) -> List[str]:
        return [item.strip() for item in re.split(r"[；;]\s*", str(value or "").strip()) if item.strip()]

    def _collect_profile_overlap(
        self,
        profile: Dict[str, Any],
        all_profiles: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        current_name = str(profile.get("name", "")).strip()
        alerts: List[str] = []
        scalar_fields = (
            "identity_anchor",
            "soul_goal",
            "temperament_type",
            "background_imprint",
            "social_mode",
            "reward_logic",
            "belief_anchor",
            "moral_bottom_line",
            "stress_response",
            "story_role",
            "others_impression",
            "restraint_threshold",
        )
        list_fields = ("decision_rules", "key_bonds", "core_traits")
        for peer_name, peer in all_profiles.items():
            if peer_name == current_name:
                continue
            for field in scalar_fields:
                current_value = self._normalize_overlap_text(profile.get(field, ""))
                peer_value = self._normalize_overlap_text(peer.get(field, ""))
                if current_value and current_value == peer_value:
                    alerts.append(f"{field} is identical to {peer_name}")
            for field in list_fields:
                current_items = self._normalize_overlap_items(profile.get(field, []))
                peer_items = self._normalize_overlap_items(peer.get(field, []))
                if current_items and current_items == peer_items:
                    alerts.append(f"{field} fully overlaps with {peer_name}")
                elif current_items and peer_items:
                    overlap = len(set(current_items) & set(peer_items)) / max(1, min(len(current_items), len(peer_items)))
                    if overlap >= 0.75:
                        alerts.append(f"{field} heavily overlaps with {peer_name}")
        return self._dedupe_texts(alerts, 12)

    @staticmethod
    def _normalize_overlap_text(value: Any) -> str:
        return re.sub(r"\s+", "", str(value or "").strip())

    def _normalize_overlap_items(self, value: Any) -> List[str]:
        if isinstance(value, list):
            items = value
        else:
            items = self._split_persona_scalar(str(value or ""))
        return [self._normalize_overlap_text(item) for item in items if self._normalize_overlap_text(item)]

    @staticmethod
    def _split_metric_map(value: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for item in re.split(r"[；;]\s*", str(value or "").strip()):
            if not item or "=" not in item:
                continue
            key, raw = item.split("=", 1)
            key_text = key.strip()
            raw_text = raw.strip()
            if not key_text:
                continue
            if re.fullmatch(r"-?\d+", raw_text):
                result[key_text] = int(raw_text)
            else:
                result[key_text] = raw_text
        return result

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0
