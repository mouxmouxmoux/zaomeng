#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

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

        affection = int(relation_state.get("affection", 5))
        trust = int(relation_state.get("trust", 5))
        hostility = int(relation_state.get("hostility", max(0, 5 - affection)))
        ambiguity = int(relation_state.get("ambiguity", 3))

        traits = [str(item).strip() for item in character_profile.get("core_traits", []) if str(item).strip()]
        speech_style = str(character_profile.get("speech_style", ""))
        has_correction = bool(similar)

        opening = self._opening_line(
            target_name=target_name,
            affection=affection,
            trust=trust,
            hostility=hostility,
            ambiguity=ambiguity,
            speech_style=speech_style,
            has_correction=has_correction,
        )
        closing = self._closing_line(
            traits=traits,
            relation_hint=relation_hint,
            affection=affection,
            trust=trust,
            hostility=hostility,
            ambiguity=ambiguity,
        )
        return f"{opening}{closing}"

    @staticmethod
    def _opening_line(
        target_name: str,
        affection: int,
        trust: int,
        hostility: int,
        ambiguity: int,
        speech_style: str,
        has_correction: bool,
    ) -> str:
        address = f"{target_name}，" if target_name else ""
        if hostility >= 7:
            return f"{address}这话我听见了，只是不想再逼近一步。"
        if affection >= 8 and trust >= 7:
            return f"{address}你既这样问，我自然要认真回你。"
        if ambiguity >= 7:
            return f"{address}这话我先留一线，不肯一下说死。"
        if has_correction:
            return f"{address}你的意思我明白，我还是按一向的心性慢慢说。"
        if "克制" in speech_style:
            return f"{address}你先别急，我把话缓一缓再说。"
        if "直白" in speech_style:
            return f"{address}你既问起，我便直说。"
        return f"{address}你既开了口，我就照实回你。"

    @staticmethod
    def _closing_line(
        traits: List[str],
        relation_hint: str,
        affection: int,
        trust: int,
        hostility: int,
        ambiguity: int,
    ) -> str:
        primary_trait = traits[0] if traits else ""
        if hostility >= 7:
            return "今日先说到这里，余下的不必多提。"
        if affection >= 8 and trust >= 7:
            if primary_trait in {"敏感", "温柔", "善良"}:
                return "你若安稳些，我心里也就安稳些。"
            return "你既挂念，我心里自然记着。"
        if ambiguity >= 7:
            return "待我再想一想，改日再把余下的话补全。"
        if trust <= 3:
            return "这事我还要再看，不便立刻说透。"
        if primary_trait in {"敏感", "克制"}:
            return "我不愿把情绪说得太满，但意思你该明白。"
        if primary_trait in {"聪慧", "谨慎"}:
            return "眼下先看一步，再定后话。"
        if relation_hint:
            return "我心里有分寸，不会把话说偏。"
        return "事情总要一层层说明白。"
