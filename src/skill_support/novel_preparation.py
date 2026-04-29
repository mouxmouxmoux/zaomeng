#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path

from src.utils.text_parser import load_novel_text, split_sentences


def prepare_novel_excerpt(
    text: str,
    *,
    max_sentences: int = 80,
    max_chars: int = 12_000,
) -> str:
    clean = str(text or "").strip()
    if not clean:
        return ""

    selected: list[str] = []
    total_chars = 0
    for sentence in split_sentences(clean):
        if len(selected) >= max_sentences:
            break
        projected = total_chars + len(sentence) + (1 if selected else 0)
        if selected and projected > max_chars:
            break
        if not selected and len(sentence) > max_chars:
            return sentence[:max_chars].strip()
        selected.append(sentence)
        total_chars = projected

    if selected:
        return "\n".join(selected).strip()
    return clean[:max_chars].strip()


def load_prepared_novel_excerpt(
    novel_path: str | Path,
    *,
    max_sentences: int = 80,
    max_chars: int = 12_000,
) -> str:
    return prepare_novel_excerpt(
        load_novel_text(str(novel_path)),
        max_sentences=max_sentences,
        max_chars=max_chars,
    )


def build_excerpt_payload(
    novel_path: str | Path,
    *,
    max_sentences: int = 80,
    max_chars: int = 12_000,
) -> dict[str, object]:
    path = Path(novel_path)
    excerpt = load_prepared_novel_excerpt(
        path,
        max_sentences=max_sentences,
        max_chars=max_chars,
    )
    return {
        "source_path": str(path),
        "source_name": path.name,
        "max_sentences": max_sentences,
        "max_chars": max_chars,
        "excerpt": excerpt,
    }
