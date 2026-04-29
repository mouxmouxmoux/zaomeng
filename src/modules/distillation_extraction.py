#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from collections import Counter, defaultdict
import re
from typing import Dict, List, Tuple

from src.utils.text_parser import split_sentences


class DistillationExtractionMixin:
    def _extract_top_characters(self, text: str) -> List[str]:
        name_pattern = re.compile(rf"([{self.common_surnames}][\u4e00-\u9fff]{{1,2}})")
        raw_names: List[str] = []
        for match in name_pattern.finditer(text):
            start = match.start()
            if start > 0 and "\u4e00" <= text[start - 1] <= "\u9fff":
                continue
            raw_names.append(match.group(1))

        disallowed = set(
            "\u4f60\u6211\u4ed6\u5979\u5b83\u4eec\u7684\u4e86\u5f97\u5730\u7740\u8fc7\u5417\u5462\u554a"
            "\u5c31\u5728\u548c\u5e76\u4e0e\u628a\u88ab\u8ba9\u5411\u5bf9\u5c06\u53c8\u5f88\u90fd\u5e76\u4e14"
        )
        candidates = []
        for name in raw_names:
            if name in self.stop_names or len(name) < 2 or len(name) > 3:
                continue
            if any(ch in disallowed for ch in name[1:]):
                continue
            candidates.append(name)

        counts = Counter(candidates)
        filtered = self._pick_frequent_names(counts, min_count=int(self.config.get("distillation.min_appearances", 3)))
        if not filtered:
            filtered = self._pick_frequent_names(counts, min_count=2)
        if not filtered:
            filtered = self._pick_frequent_names(counts, min_count=1)

        if len(filtered) < 3:
            alias_candidates = re.findall(
                r"[\u4e00-\u9fff]{2}(?:\u513f|\u54e5|\u59d0|\u59b9|\u516c|\u7237)?",
                text,
            )
            for alias, count in Counter(alias_candidates).most_common(10):
                if count < 2 or alias in self.stop_names or alias in filtered:
                    continue
                filtered.append(alias)

        return filtered[: int(self.config.get("distillation.max_characters", 10))]

    def _pick_frequent_names(self, counts: Counter[str], min_count: int) -> List[str]:
        filtered: List[str] = []
        for name, count in counts.most_common(60):
            if count < min_count:
                continue
            if self._looks_like_name(name):
                filtered.append(name)
        return filtered

    def _build_alias_map(
        self,
        text: str,
        character_names: List[str],
        allow_sparse_alias: bool = False,
    ) -> Dict[str, List[str]]:
        alias_owners: Dict[str, List[str]] = defaultdict(list)
        for name in character_names:
            for alias in self.candidate_aliases(name):
                alias_owners[alias].append(name)

        alias_map: Dict[str, List[str]] = {}
        for name in character_names:
            aliases = [name]
            for alias in self.candidate_aliases(name):
                if alias_owners.get(alias) != [name]:
                    continue
                if not self._alias_is_reliable(text, alias, allow_sparse_alias=allow_sparse_alias):
                    continue
                aliases.append(alias)
            alias_map[name] = self._unique_texts(aliases)
        return alias_map

    def _alias_is_reliable(self, text: str, alias: str, allow_sparse_alias: bool = False) -> bool:
        if len(alias) < 2 or alias in self.stop_names:
            return False
        min_mentions = 1 if allow_sparse_alias else 2
        return self._count_token_mentions(text, alias) >= min_mentions

    def _extract_from_chunk(
        self,
        chunk: str,
        alias_map: Dict[str, List[str]],
    ) -> Tuple[Dict[str, Dict[str, List[str]]], Dict[str, Dict[str, int]]]:
        sentences = split_sentences(chunk)
        evidence_map: Dict[str, Dict[str, List[str]]] = {}
        value_map: Dict[str, Dict[str, int]] = {}
        dims = self._value_dimensions()

        for name, aliases in alias_map.items():
            evidence = self._empty_bucket()
            values_acc: List[Dict[str, int]] = []

            for idx, sentence in enumerate(sentences):
                if self._looks_like_metadata_sentence(sentence):
                    continue
                prev_sent = sentences[idx - 1] if idx > 0 else ""
                next_sent = sentences[idx + 1] if idx + 1 < len(sentences) else ""
                contains_name = self._text_mentions_any_alias(sentence, aliases)
                pronoun_hit = any(token in sentence for token in ("\u4ed6", "\u5979")) and (
                    self._text_mentions_any_alias(prev_sent, aliases) or self._text_mentions_any_alias(next_sent, aliases)
                )
                has_quote = "\u201c" in sentence or "\"" in sentence
                speaker_hit = has_quote and self._is_likely_spoken_by(sentence, aliases, prev_sent, next_sent)

                if not (contains_name or pronoun_hit or speaker_hit):
                    continue

                if has_quote and speaker_hit:
                    spoken = self._extract_spoken_content(sentence, aliases, prev_sent, next_sent)
                    if spoken:
                        evidence["dialogues"].append(spoken)
                        values_acc.append(self._score_values(spoken, dims))
                    continue

                if any(
                    token in sentence
                    for token in ("\u5fc3\u60f3", "\u60f3\u7740", "\u89c9\u5f97", "\u6697\u9053", "\u5fc3\u91cc")
                ):
                    evidence["thoughts"].append(sentence)
                else:
                    evidence["descriptions"].append(sentence)
                values_acc.append(self._score_values(sentence, dims))

            if any(evidence.values()):
                filtered_evidence = self._filter_character_specific_evidence(evidence, aliases, alias_map)
                evidence_map[name] = {
                    key: self._dedupe_texts(items, limit=24 if key == "descriptions" else 12)
                    for key, items in filtered_evidence.items()
                }
                value_map[name] = self._average_values(values_acc, dims)

        return evidence_map, value_map

    def _filter_character_specific_evidence(
        self,
        evidence: Dict[str, List[str]],
        aliases: List[str],
        alias_map: Dict[str, List[str]],
    ) -> Dict[str, List[str]]:
        filtered = {
            "descriptions": [],
            "dialogues": list(evidence.get("dialogues", [])),
            "thoughts": [],
        }
        for key in ("descriptions", "thoughts"):
            for sentence in evidence.get(key, []):
                mentioned_names = self._mentioned_characters_in_sentence(sentence, alias_map)
                if len(mentioned_names) <= 1:
                    filtered[key].append(sentence)
                    continue
                if self._sentence_centers_character(sentence, aliases):
                    filtered[key].append(sentence)
        return filtered

    def _mentioned_characters_in_sentence(
        self,
        sentence: str,
        alias_map: Dict[str, List[str]],
    ) -> List[str]:
        hits: List[str] = []
        for name, aliases in alias_map.items():
            if self._text_mentions_any_alias(sentence, aliases):
                hits.append(name)
        return hits

    @staticmethod
    def _sentence_centers_character(sentence: str, aliases: List[str]) -> bool:
        text = str(sentence or "").strip()
        if not text:
            return False
        lead_chars = "\"\u201c\u2018\uff08("
        action_tokens = (
            "\u5fc3\u60f3",
            "\u60f3\u7740",
            "\u89c9\u5f97",
            "\u6697\u9053",
            "\u5fc3\u91cc",
            "\u8bf4\u9053",
            "\u95ee\u9053",
            "\u7b11\u9053",
            "\u770b\u7740",
            "\u76ef\u7740",
            "\u671b\u7740",
            "\u671d\u7740",
            "\u5bf9\u7740",
            "\u8d70\u5411",
            "\u4f38\u624b",
            "\u6294\u624b",
            "\u5f00\u53e3",
        )
        for alias in aliases:
            if text.lstrip(lead_chars).startswith(alias):
                return True
            if any(f"{alias}{token}" in text for token in action_tokens):
                return True
        return False

    def _score_values(self, sentence: str, dims: List[str]) -> Dict[str, int]:
        score = {dim: 5 for dim in dims}
        for dim in dims:
            config = self.value_markers.get(dim, {})
            positive = sum(sentence.count(token) for token in config.get("positive", []))
            negative = sum(sentence.count(token) for token in config.get("negative", []))
            delta = min(3, positive) - min(3, negative)
            score[dim] = max(1, min(10, score[dim] + delta))
        return score

    @staticmethod
    def _average_values(values_list: List[Dict[str, int]], dims: List[str]) -> Dict[str, int]:
        if not values_list:
            return {dim: 5 for dim in dims}
        averaged: Dict[str, int] = {}
        for dim in dims:
            averaged[dim] = int(round(sum(item.get(dim, 5) for item in values_list) / len(values_list)))
        return averaged
