#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import re
from pathlib import Path
from typing import List


def _strip_html_tags(text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def load_novel_text(path: str) -> str:
    novel_path = Path(path)
    if not novel_path.exists():
        raise FileNotFoundError(f"小说文件不存在: {path}")

    suffix = novel_path.suffix.lower()
    if suffix == ".txt":
        return novel_path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".epub":
        return _load_epub(novel_path)
    raise ValueError(f"不支持的文件类型: {suffix}，仅支持 .txt / .epub")


def _load_epub(path: Path) -> str:
    try:
        from ebooklib import epub
    except Exception as exc:
        raise RuntimeError("读取 .epub 需要安装 ebooklib") from exc

    book = epub.read_epub(str(path))
    chunks: List[str] = []
    for item in book.get_items():
        if item.get_type() == 9:  # ebooklib.ITEM_DOCUMENT
            html = item.get_content().decode("utf-8", errors="ignore")
            text = _strip_html_tags(html)
            if text:
                chunks.append(text)
    return "\n".join(chunks)


def split_sentences(text: str) -> List[str]:
    if not text:
        return []
    parts = re.split(r"(?<=[。！？!?；;])\s*", text)
    return [p.strip() for p in parts if p.strip()]

