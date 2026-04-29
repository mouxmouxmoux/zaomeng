#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any, Dict, List, Tuple


class DistillationProfileBuilderMixin:
    def _build_profile(
        self,
        name: str,
        bucket: Dict[str, List[str]],
        arc_values: List[Tuple[int, Dict[str, int]]],
    ) -> Dict[str, Any]:
        character_hint = self._resolve_character_hint(name)
        descriptions = self._dedupe_texts(bucket["descriptions"], 24)
        dialogues = self._dedupe_texts(bucket["dialogues"], 8)
        thoughts = self._dedupe_texts(bucket["thoughts"], 12)
        timeline = list(bucket.get("timeline", []))
        evidence_lines = self._dedupe_texts([*descriptions, *thoughts, *dialogues], 32)
        narrative_lines = self._dedupe_texts([*descriptions, *thoughts], 16)
        archetype = self._infer_archetype(name, descriptions, dialogues, thoughts)
        values = self._infer_values_from_corpus(self._merge_arc_values(arc_values), descriptions, dialogues, thoughts, archetype)
        core_traits = self._infer_traits(descriptions + dialogues + thoughts, archetype)
        speech_style = self._infer_speech_style(dialogues, archetype)
        decision_rules = self._dedupe_texts([*thoughts, *descriptions, *dialogues], 8)
        if not decision_rules:
            decision_rules = self._infer_decision_rules(thoughts, descriptions, dialogues, archetype)
        arc = self._build_arc(arc_values, values, timeline)
        life_experience = narrative_lines[:4] or dialogues[:2]
        if not life_experience:
            life_experience = [name]
        identity_anchor = narrative_lines[0] if narrative_lines else (dialogues[0] if dialogues else name)
        soul_goal = thoughts[0] if thoughts else (decision_rules[0] if decision_rules else identity_anchor)
        trauma_scar = thoughts[0] if thoughts else self._infer_trauma_scar(life_experience, thoughts, descriptions, archetype)
        worldview = thoughts[0] if thoughts else (descriptions[0] if descriptions else soul_goal)
        thinking_style = self._infer_thinking_style(values, core_traits, speech_style, archetype)
        speech_habits = self._infer_speech_habits(dialogues, speech_style)
        emotion_profile = self._infer_emotion_profile(dialogues, thoughts, speech_style, core_traits)
        temperament_type = self._infer_temperament_type(core_traits, speech_style, values, archetype)
        taboo_topics = self._infer_taboo_topics(values, core_traits, decision_rules)
        forbidden_behaviors = self._infer_forbidden_behaviors(values, core_traits, speech_style)
        core_identity = descriptions[0] if descriptions else identity_anchor
        faction_position = self._infer_faction_position(name, descriptions, dialogues, thoughts, values)
        background_imprint = life_experience[0] if life_experience else identity_anchor
        world_rule_fit = self._infer_world_rule_fit(values, decision_rules, speech_style)
        strengths = self._infer_strengths(core_traits, decision_rules, speech_style)
        weaknesses = self._infer_weaknesses(core_traits, emotion_profile, speech_style)
        cognitive_limits = self._infer_cognitive_limits(values, core_traits)
        action_style = descriptions[0] if descriptions else (dialogues[0] if dialogues else speech_style)
        social_mode = dialogues[0] if dialogues else (descriptions[0] if descriptions else identity_anchor)
        key_bonds = self._infer_key_bonds(values, decision_rules, taboo_topics)
        reward_logic = decision_rules[0] if decision_rules else worldview
        hidden_desire = thoughts[0] if thoughts else soul_goal
        inner_conflict = thoughts[1] if len(thoughts) > 1 else hidden_desire
        fear_triggers = self._infer_fear_triggers(values, taboo_topics, forbidden_behaviors)
        private_self = thoughts[0] if thoughts else self._infer_private_self(speech_style, emotion_profile, social_mode)
        story_role = descriptions[0] if descriptions else self._infer_story_role(descriptions, dialogues, thoughts, decision_rules)
        belief_anchor = worldview
        stance_stability = self._infer_stance_stability(values, decision_rules)
        moral_bottom_line = forbidden_behaviors[0] if forbidden_behaviors else belief_anchor
        self_cognition = thoughts[0] if thoughts else identity_anchor
        stress_response = thoughts[0] if thoughts else self._infer_stress_response(
            emotion_profile,
            decision_rules,
            speech_style,
            forbidden_behaviors,
            archetype,
        )
        others_impression = descriptions[0] if descriptions else (speech_style or identity_anchor)
        restraint_threshold = forbidden_behaviors[0] if forbidden_behaviors else (thoughts[0] if thoughts else hidden_desire)

        profile = {
            "name": name,
            "core_traits": core_traits[: int(self.config.get("distillation.traits_max_count", 10))],
            "values": values,
            "speech_style": speech_style,
            "typical_lines": dialogues[:8],
            "decision_rules": decision_rules[:8],
            "identity_anchor": identity_anchor,
            "soul_goal": soul_goal,
            "life_experience": life_experience[:4],
            "trauma_scar": trauma_scar,
            "worldview": worldview,
            "thinking_style": thinking_style,
            "temperament_type": temperament_type,
            "speech_habits": speech_habits,
            "emotion_profile": emotion_profile,
            "taboo_topics": taboo_topics[:6],
            "forbidden_behaviors": forbidden_behaviors[:6],
            "core_identity": core_identity,
            "faction_position": faction_position,
            "background_imprint": background_imprint,
            "world_rule_fit": world_rule_fit,
            "strengths": strengths[:5],
            "weaknesses": weaknesses[:5],
            "cognitive_limits": cognitive_limits[:4],
            "action_style": action_style,
            "social_mode": social_mode,
            "key_bonds": key_bonds[:4],
            "reward_logic": reward_logic,
            "hidden_desire": hidden_desire,
            "inner_conflict": inner_conflict,
            "fear_triggers": fear_triggers[:5],
            "private_self": private_self,
            "story_role": story_role,
            "belief_anchor": belief_anchor,
            "moral_bottom_line": moral_bottom_line,
            "self_cognition": self_cognition,
            "stress_response": stress_response,
            "others_impression": others_impression,
            "restraint_threshold": restraint_threshold,
            "stance_stability": stance_stability,
            "arc": arc,
            "arc_summary": self._infer_arc_summary(arc),
            "arc_confidence": self._infer_arc_confidence(arc, timeline),
            "archetype": archetype,
            "evidence_excerpt": evidence_lines[:8],
        }
        return self._apply_character_hint(profile, character_hint)
