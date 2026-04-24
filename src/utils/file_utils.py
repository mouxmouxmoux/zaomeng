#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional


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


def save_json(path: str | Path, data: Dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def safe_filename(name: str) -> str:
    clean = re.sub(r"[\\/:*?\"<>|]", "_", name).strip()
    return clean or "unnamed"


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
