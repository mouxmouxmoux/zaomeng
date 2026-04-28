#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Optional

from src.core.config import Config
from src.core.llm_client import LLMClient
from src.core.path_provider import PathProvider
from src.core.rulebook import RuleBook
from src.modules.chat_engine import ChatEngine
from src.modules.distillation import NovelDistiller
from src.modules.reflection import ReflectionEngine
from src.modules.relationships import RelationshipExtractor
from src.modules.speaker import Speaker
from src.utils.token_counter import TokenCounter


@dataclass
class RuntimeParts:
    config: Config
    path_provider: PathProvider
    rulebook: RuleBook
    llm: LLMClient
    token_counter: TokenCounter
    _reflection: Optional[ReflectionEngine] = None
    _distiller: Optional[NovelDistiller] = None
    _speaker: Optional[Speaker] = None
    _extractor: Optional[RelationshipExtractor] = None
    _chat_engine: Optional[ChatEngine] = None

    def create_reflection(self) -> ReflectionEngine:
        if self._reflection is None:
            self._reflection = ReflectionEngine.from_runtime_parts(self)
        return self._reflection

    @property
    def reflection(self) -> ReflectionEngine:
        return self.create_reflection()

    @reflection.setter
    def reflection(self, value: Optional[ReflectionEngine]) -> None:
        self._reflection = value

    def create_distiller(self) -> NovelDistiller:
        if self._distiller is None:
            self._distiller = NovelDistiller.from_runtime_parts(self)
        return self._distiller

    @property
    def distiller(self) -> NovelDistiller:
        return self.create_distiller()

    @distiller.setter
    def distiller(self, value: Optional[NovelDistiller]) -> None:
        self._distiller = value

    def create_speaker(self) -> Speaker:
        if self._speaker is None:
            self._speaker = Speaker.from_runtime_parts(self)
        return self._speaker

    @property
    def speaker(self) -> Speaker:
        return self.create_speaker()

    @speaker.setter
    def speaker(self, value: Optional[Speaker]) -> None:
        self._speaker = value

    def create_extractor(self) -> RelationshipExtractor:
        if self._extractor is None:
            self._extractor = RelationshipExtractor.from_runtime_parts(self)
        return self._extractor

    @property
    def extractor(self) -> RelationshipExtractor:
        return self.create_extractor()

    @extractor.setter
    def extractor(self, value: Optional[RelationshipExtractor]) -> None:
        self._extractor = value

    def build_chat_engine(self, chat_engine_cls: type[ChatEngine] = ChatEngine) -> ChatEngine:
        return chat_engine_cls(
            self.config,
            llm=self.llm,
            reflection=self.reflection,
            speaker=self.speaker,
            distiller=self.distiller,
            rulebook=self.rulebook,
            path_provider=self.path_provider,
        )

    def create_chat_engine(self) -> ChatEngine:
        if self._chat_engine is None:
            self._chat_engine = self.build_chat_engine()
        return self._chat_engine

    @property
    def chat_engine(self) -> ChatEngine:
        return self.create_chat_engine()

    @chat_engine.setter
    def chat_engine(self, value: Optional[ChatEngine]) -> None:
        self._chat_engine = value

    def shared_dependency_overrides(self) -> "RuntimeDependencyOverrides":
        return RuntimeDependencyOverrides(
            path_provider=self.path_provider,
            rulebook=self.rulebook,
            llm=self.llm,
            token_counter=self.token_counter,
        )

    def fork(self, overrides: Optional["RuntimeDependencyOverrides"] = None) -> "RuntimeParts":
        return build_runtime_parts(
            self.config,
            overrides=self.shared_dependency_overrides().merged_with(overrides),
        )


@dataclass
class RuntimeDependencyOverrides:
    path_provider: Optional[PathProvider] = None
    rulebook: Optional[RuleBook] = None
    llm: Optional[LLMClient] = None
    token_counter: Optional[TokenCounter] = None
    reflection: Optional[ReflectionEngine] = None
    distiller: Optional[NovelDistiller] = None
    speaker: Optional[Speaker] = None
    extractor: Optional[RelationshipExtractor] = None
    chat_engine: Optional[ChatEngine] = None

    def merged_with(self, other: Optional["RuntimeDependencyOverrides"] = None) -> "RuntimeDependencyOverrides":
        current = {item.name: getattr(self, item.name) for item in fields(self)}
        if other is None:
            return RuntimeDependencyOverrides(**current)
        merged = dict(current)
        for item in fields(other):
            key = item.name
            value = getattr(other, key)
            if value is not None:
                merged[key] = value
        return RuntimeDependencyOverrides(**merged)


def build_runtime_parts(
    config: Optional[Config] = None,
    *,
    overrides: Optional[RuntimeDependencyOverrides] = None,
) -> RuntimeParts:
    resolved_config = config or Config()
    resolved_overrides = overrides or RuntimeDependencyOverrides()
    path_provider = resolved_overrides.path_provider or PathProvider(resolved_config)
    rulebook = resolved_overrides.rulebook or RuleBook(resolved_config, path_provider=path_provider)
    llm = resolved_overrides.llm or LLMClient(resolved_config)
    token_counter = resolved_overrides.token_counter or TokenCounter()
    parts = RuntimeParts(
        config=resolved_config,
        path_provider=path_provider,
        rulebook=rulebook,
        llm=llm,
        token_counter=token_counter,
        _reflection=resolved_overrides.reflection,
        _distiller=resolved_overrides.distiller,
        _speaker=resolved_overrides.speaker,
        _extractor=resolved_overrides.extractor,
        _chat_engine=resolved_overrides.chat_engine,
    )
    return parts
