#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

NOISE_NAME_SUFFIXES = {"说", "道", "笑", "听", "问", "看", "想", "叹", "喊", "叫", "哭", "忙"}


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_json(path: str | Path, default: Any = None) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def _sanitize_json_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.encode("utf-8", errors="replace").decode("utf-8")
    if isinstance(value, list):
        return [_sanitize_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize_json_value(item) for item in value]
    if isinstance(value, dict):
        return {
            _sanitize_json_value(key): _sanitize_json_value(item)
            for key, item in value.items()
        }
    return value


def save_json(path: str | Path, data: Dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(_sanitize_json_value(data), f, ensure_ascii=False, indent=2)


def safe_filename(name: str) -> str:
    clean = re.sub(r"[\\/:*?\"<>|]", "_", name).strip()
    return clean or "unnamed"


def normalize_character_name(name: str) -> str:
    clean = str(name or "").strip()
    if len(clean) >= 3 and clean[-1] in NOISE_NAME_SUFFIXES:
        return clean[:-1]
    return clean


def normalize_relation_key(key: str) -> str:
    parts = [normalize_character_name(part) for part in str(key).split("_") if part]
    if len(parts) != 2:
        return str(key)
    return "_".join(sorted(parts))


def novel_id_from_input(novel: str) -> str:
    raw = Path(novel).stem if Path(novel).suffix else Path(novel).name
    if not raw:
        raw = novel
    return safe_filename(raw)


def find_character_file(
    base_dir: str | Path,
    character_name: str,
    novel_id: Optional[str] = None,
) -> list[Path]:
    root = Path(base_dir)
    filename = f"{safe_filename(character_name)}.json"

    if novel_id:
        scoped = root / novel_id / filename
        return [scoped] if scoped.exists() else []

    matches = list(root.glob(filename))
    matches.extend(root.glob(f"*/{filename}"))
    return sorted({path.resolve() for path in matches})
