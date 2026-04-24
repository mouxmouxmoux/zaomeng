#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from src.core.config import Config
from src.modules.reflection import ReflectionEngine


class Speaker:
    """Character utterance generator with correction-memory retrieval."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.reflection = ReflectionEngine(self.config)

    def generate(
        self,
        character_profile: Dict[str, Any],
        context: str,
        history: List[Dict[str, str]],
        target_name: str = "",
        relation_state: Optional[Dict[str, Any]] = None,
        relation_hint: str = "",
    ) -> str:
        name = character_profile.get("name", "角色")
        relation_state = relation_state or {}
        recent = history[-6:]
        recent_text = "\n".join(f"{x['speaker']}: {x['message']}" for x in recent)
        similar = self.reflection.search_similar_corrections(
            recent_text,
            character=name,
            target=target_name or None,
            top_k=2,
        )
        correction_hint = "\n".join(
            f"避免: {x.get('original_message')} -> 倾向: {x.get('corrected_message')}" for x in similar
        )

        affection = int(relation_state.get("affection", 5))
        trust = int(relation_state.get("trust", 5))
        hostility = int(relation_state.get("hostility", max(0, 5 - affection)))
        ambiguity = int(relation_state.get("ambiguity", 3))

        # Fully local deterministic generation with target-specific tone.
        choices = character_profile.get("typical_lines", [])[:5]
        suffix = self._relation_suffix(
            speech_style=character_profile.get("speech_style", ""),
            target_name=target_name,
            affection=affection,
            trust=trust,
            hostility=hostility,
            ambiguity=ambiguity,
            has_correction=bool(correction_hint),
        )
        if choices:
            base = random.choice(choices)
            return f"{base}（{suffix}）"

        traits = "、".join(character_profile.get("core_traits", [])[:2]) or "克制"
        if relation_hint:
            return f"{name}（{traits}）对{target_name or '对方'}回应：{self._relation_sentence(affection, hostility, trust, ambiguity)}"
        return f"{name}（{traits}）回应：{self._relation_sentence(affection, hostility, trust, ambiguity)}"

    @staticmethod
    def _relation_suffix(
        speech_style: str,
        target_name: str,
        affection: int,
        trust: int,
        hostility: int,
        ambiguity: int,
        has_correction: bool,
    ) -> str:
        if has_correction:
            return f"对{target_name or '对方'}时，我会按纠错原则收束表达。"
        if hostility >= 7:
            return f"对{target_name or '对方'}保持明显距离和锋芒。"
        if affection >= 8 and trust >= 7:
            return f"对{target_name or '对方'}语气更软，会照顾对方情绪。"
        if ambiguity >= 7:
            return f"对{target_name or '对方'}带试探，不把话说满。"
        if "克制" in speech_style:
            return f"对{target_name or '对方'}先收住情绪，再表达立场。"
        return "这是我此刻的态度。"

    @staticmethod
    def _relation_sentence(affection: int, hostility: int, trust: int, ambiguity: int) -> str:
        if hostility >= 7:
            return "话我会说，但不会给你太多余地。"
        if affection >= 8 and trust >= 7:
            return "我先顾着你的感受，再把事情说开。"
        if ambiguity >= 7:
            return "我先试探你的意思，再决定把话说到哪一步。"
        if trust <= 3:
            return "我会先留几分，不会轻易把底牌交出去。"
        return "先把话说清，再看彼此立场。"
