#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.config import Config
from src.core.llm_client import LLMClient
from src.modules.reflection import ReflectionEngine
from src.modules.speaker import Speaker
from src.utils.file_utils import ensure_dir, load_json, save_json


class ChatEngine:
    """Multi-character chat with observe/act modes and inline commands."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.llm = LLMClient(self.config)
        self.reflection = ReflectionEngine(self.config)
        self.speaker = Speaker(self.config)
        self.characters_dir = Path(self.config.get_path("characters"))
        self.sessions_dir = ensure_dir(self.config.get_path("sessions"))
        self.relations_dir = ensure_dir(self.config.get_path("relations"))

    def create_session(self, novel: str, mode: str) -> Dict[str, Any]:
        profiles = self._load_character_profiles()
        if not profiles:
            raise RuntimeError("未找到角色档案，请先运行 distill。")
        characters = list(profiles.keys())
        session = {
            "id": uuid.uuid4().hex[:12],
            "title": f"{novel}_{mode}_{int(time.time())}",
            "novel": novel,
            "mode": mode,
            "created_at": int(time.time()),
            "characters": characters,
            "history": [],
            "state": {
                "emotion": {},
                "relation_delta": {},
                "relation_matrix": self._build_relation_matrix(characters),
            },
        }
        self._save_session(session)
        return session

    def restore_session(self, session_id: str) -> Dict[str, Any]:
        path = self.sessions_dir / f"{session_id}.json"
        data = load_json(path, default=None)
        if not data:
            raise FileNotFoundError(f"会话不存在: {session_id}")
        return data

    def observe_mode(self, session: Dict[str, Any]) -> None:
        print("进入 observe 模式。输入 /save /reflect /correct /quit")
        while True:
            user_msg = input("\n你: ").strip()
            if not user_msg:
                continue
            if self._handle_inline_command(session, user_msg):
                if user_msg == "/quit":
                    break
                continue

            session["history"].append({"speaker": "旁白", "message": user_msg, "ts": int(time.time())})
            profiles = self._load_character_profiles()
            for name in session["characters"][:4]:
                profile = profiles.get(name, {"name": name})
                target_name = self._infer_target(name, session["history"], session["characters"])
                relation_state = self._get_relation_state(session, name, target_name)
                reply = self.speaker.generate(
                    character_profile=profile,
                    context=user_msg,
                    history=session["history"],
                    target_name=target_name,
                    relation_state=relation_state,
                    relation_hint=self._relation_hint(name, session["characters"]),
                )
                reply = self._guard_reply(profile, reply, relation_state, target_name)
                print(f"{name}: {reply}")
                session["history"].append(
                    {"speaker": name, "target": target_name, "message": reply, "ts": int(time.time())}
                )

            self._update_state(session)
            self._save_session(session)
            self._print_turn_cost()

    def act_mode(self, session: Dict[str, Any], character: str) -> None:
        print(f"进入 act 模式，你扮演 {character}。输入 /save /reflect /correct /quit")
        while True:
            user_msg = input(f"\n{character}(你): ").strip()
            if not user_msg:
                continue
            if self._handle_inline_command(session, user_msg):
                if user_msg == "/quit":
                    break
                continue

            session["history"].append({"speaker": character, "message": user_msg, "ts": int(time.time())})
            profiles = self._load_character_profiles()
            for name in session["characters"][:4]:
                if name == character:
                    continue
                profile = profiles.get(name, {"name": name})
                target_name = self._infer_target(name, session["history"], session["characters"])
                relation_state = self._get_relation_state(session, name, target_name)
                reply = self.speaker.generate(
                    character_profile=profile,
                    context=user_msg,
                    history=session["history"],
                    target_name=target_name,
                    relation_state=relation_state,
                    relation_hint=self._relation_hint(name, session["characters"]),
                )
                reply = self._guard_reply(profile, reply, relation_state, target_name)
                print(f"{name}: {reply}")
                session["history"].append(
                    {"speaker": name, "target": target_name, "message": reply, "ts": int(time.time())}
                )

            self._update_state(session)
            self._save_session(session)
            self._print_turn_cost()

    def _handle_inline_command(self, session: Dict[str, Any], command: str) -> bool:
        if command == "/quit":
            self._save_session(session)
            print("会话结束。")
            return True
        if command == "/save":
            self._save_session(session)
            print(f"已保存会话: {session['id']}")
            return True
        if command == "/reflect":
            self._reflect_last_turn(session)
            return True
        if command.startswith("/correct"):
            # /correct 角色|对象|原句|修正句|原因
            payload = command[len("/correct") :].strip()
            parts = [p.strip() for p in payload.split("|")]
            if len(parts) not in (3, 4, 5):
                print("格式错误。用法: /correct 角色|对象|原句|修正句|原因")
                return True
            if len(parts) == 3:
                character, target, original, corrected, reason = parts[0], "", parts[1], parts[2], "inline_command"
            elif len(parts) == 4:
                character, target, original, corrected, reason = parts[0], parts[1], parts[2], parts[3], "inline_command"
            else:
                character, target, original, corrected, reason = parts[0], parts[1], parts[2], parts[3], parts[4]
            item = self.reflection.save_correction(
                session_id=session["id"],
                character=character,
                target=target or None,
                original_message=original,
                corrected_message=corrected,
                reason=reason,
            )
            print(f"纠错已记录: {item['character']} -> {item.get('target') or '任意对象'}")
            return True
        return False

    def _reflect_last_turn(self, session: Dict[str, Any]) -> None:
        if not session["history"]:
            print("无历史可反思。")
            return
        profiles = self._load_character_profiles()
        last = session["history"][-1]
        profile = profiles.get(last["speaker"])
        if not profile:
            print("最近一条不是角色发言。")
            return
        check = self.reflection.detect_ooc(profile, last["message"])
        if not check.is_ooc:
            print("反思结果：最近发言符合人设。")
            return
        print("反思结果：疑似 OOC")
        for reason in check.reasons:
            print(f"- {reason}")

    def _relation_hint(self, speaker: str, all_chars: List[str]) -> str:
        hints = []
        for other in all_chars:
            if other == speaker:
                continue
            item = self._get_relation_state_from_disk(speaker, other)
            if item:
                hints.append(
                    f"{other}(trust={item.get('trust',5)},aff={item.get('affection',5)},host={item.get('hostility', max(0, 5-item.get('affection',5)))})"
                )
        return "; ".join(hints[:3])

    def _latest_relations_file(self) -> Optional[Path]:
        files = sorted(self.relations_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        return files[0] if files else None

    def _update_state(self, session: Dict[str, Any]) -> None:
        latest = session["history"][-6:]
        emotion = session["state"]["emotion"]
        relation_matrix = session["state"].setdefault("relation_matrix", {})
        for item in latest:
            speaker = item["speaker"]
            if speaker in ("旁白", "用户"):
                continue
            delta = 0
            msg = item["message"]
            if any(k in msg for k in ("！", "愤怒", "生气", "质问")):
                delta += 1
            if any(k in msg for k in ("冷静", "平静", "慢慢说", "理解")):
                delta -= 1
            emotion[speaker] = max(-5, min(5, emotion.get(speaker, 0) + delta))
            target = item.get("target") or self._infer_target(speaker, latest, session["characters"])
            if target and target != speaker:
                key = self._pair_key(speaker, target)
                state = relation_matrix.setdefault(
                    key,
                    {"trust": 5, "affection": 5, "hostility": 0, "ambiguity": 3},
                )
                if any(k in msg for k in ("谢谢", "抱歉", "理解", "关心", "在意")):
                    state["affection"] = min(10, state.get("affection", 5) + 1)
                    state["trust"] = min(10, state.get("trust", 5) + 1)
                    state["hostility"] = max(0, state.get("hostility", 0) - 1)
                if any(k in msg for k in ("滚", "讨厌", "厌恶", "闭嘴", "烦")):
                    state["hostility"] = min(10, state.get("hostility", 0) + 2)
                    state["affection"] = max(0, state.get("affection", 5) - 2)
                    state["trust"] = max(0, state.get("trust", 5) - 1)
                if any(k in msg for k in ("也许", "或许", "未必", "以后再说")):
                    state["ambiguity"] = min(10, state.get("ambiguity", 3) + 1)
                session["state"]["relation_delta"][key] = {
                    "trust": state["trust"],
                    "affection": state["affection"],
                    "hostility": state["hostility"],
                    "ambiguity": state["ambiguity"],
                }

    def _print_turn_cost(self) -> None:
        summary = self.llm.get_cost_summary()
        print(
            f"[本轮后累计] token={summary['total_tokens']} "
            f"session=${summary['session_cost']:.4f} daily=${summary['daily_cost']:.4f}"
        )

    def _save_session(self, session: Dict[str, Any]) -> None:
        save_json(self.sessions_dir / f"{session['id']}.json", session)

    def _load_character_profiles(self) -> Dict[str, Dict[str, Any]]:
        profiles: Dict[str, Dict[str, Any]] = {}
        if not self.characters_dir.exists():
            return profiles
        for file in self.characters_dir.glob("*.json"):
            item = load_json(file, default=None)
            if item and isinstance(item, dict) and item.get("name"):
                profiles[item["name"]] = item
        return profiles

    @staticmethod
    def _pair_key(a: str, b: str) -> str:
        return "_".join(sorted([a, b]))

    def _build_relation_matrix(self, characters: List[str]) -> Dict[str, Dict[str, Any]]:
        matrix: Dict[str, Dict[str, Any]] = {}
        for speaker in characters:
            for target in characters:
                if speaker == target:
                    continue
                disk = self._get_relation_state_from_disk(speaker, target) or {}
                matrix[self._pair_key(speaker, target)] = {
                    "trust": int(disk.get("trust", 5)),
                    "affection": int(disk.get("affection", 5)),
                    "hostility": int(disk.get("hostility", max(0, 5 - int(disk.get("affection", 5))))),
                    "ambiguity": int(disk.get("ambiguity", 3)),
                }
        return matrix

    def _get_relation_state_from_disk(self, speaker: str, target: str) -> Dict[str, Any]:
        rel_file = self._latest_relations_file()
        if not rel_file:
            return {}
        rel = load_json(rel_file, default={})
        return rel.get(self._pair_key(speaker, target), {})

    def _get_relation_state(self, session: Dict[str, Any], speaker: str, target: str) -> Dict[str, Any]:
        if not target:
            return {}
        matrix = session["state"].setdefault("relation_matrix", {})
        return matrix.get(self._pair_key(speaker, target), {})

    @staticmethod
    def _infer_target(speaker: str, history: List[Dict[str, Any]], all_chars: List[str]) -> str:
        for item in reversed(history):
            prev_speaker = item.get("speaker", "")
            if prev_speaker and prev_speaker != speaker and prev_speaker in all_chars:
                return prev_speaker
        for candidate in all_chars:
            if candidate != speaker:
                return candidate
        return ""

    def _guard_reply(
        self,
        profile: Dict[str, Any],
        reply: str,
        relation_state: Dict[str, Any],
        target_name: str,
    ) -> str:
        issues = self.reflection.relation_alignment_issues(reply, relation_state)
        checked = self.reflection.detect_ooc(profile, reply)
        if not issues and not checked.is_ooc:
            return reply

        rewritten = self._rewrite_reply(reply, relation_state, target_name)
        issues_after = self.reflection.relation_alignment_issues(rewritten, relation_state)
        checked_after = self.reflection.detect_ooc(profile, rewritten)
        if issues_after or checked_after.is_ooc:
            reasons = issues_after + checked_after.reasons
            return f"{rewritten}（needs_revision: {'; '.join(reasons[:2])}）"
        return rewritten

    @staticmethod
    def _rewrite_reply(reply: str, relation_state: Dict[str, Any], target_name: str) -> str:
        hostility = int(relation_state.get("hostility", 0))
        affection = int(relation_state.get("affection", 5))
        ambiguity = int(relation_state.get("ambiguity", 3))
        if hostility >= 7:
            return f"对{target_name or '对方'}，我把话说到这里，不必更近一步。"
        if affection >= 8:
            return f"对{target_name or '对方'}，我会把语气放缓，把话说明白。"
        if ambiguity >= 7:
            return f"对{target_name or '对方'}，我先留一点余地，不把话说死。"
        return f"{reply}（已按对象关系收束）"
