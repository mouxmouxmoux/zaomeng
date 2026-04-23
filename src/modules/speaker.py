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
        relation_hint: str = "",
    ) -> str:
        name = character_profile.get("name", "角色")
        recent = history[-6:]
        recent_text = "\n".join(f"{x['speaker']}: {x['message']}" for x in recent)
        similar = self.reflection.search_similar_corrections(recent_text, character=name, top_k=2)
        correction_hint = "\n".join(
            f"避免: {x.get('original_message')} -> 倾向: {x.get('corrected_message')}" for x in similar
        )

        # Fully local deterministic generation.
        choices = character_profile.get("typical_lines", [])[:5]
        if choices:
            base = random.choice(choices)
            suffix = "我先这样回应。" if "克制" in character_profile.get("speech_style", "") else "这是我的态度。"
            if correction_hint:
                suffix = "我会按纠错原则收束表达。"
            return f"{base}（{suffix}）"

        traits = "、".join(character_profile.get("core_traits", [])[:2]) or "克制"
        if relation_hint:
            return f"{name}（{traits}）回应：先把话说清，再看彼此立场。"
        return f"{name}（{traits}）回应：我会按我的原则处理这件事。"
