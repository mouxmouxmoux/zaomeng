#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from src.core.contracts import PathProviderLike, RelationStore
from src.utils.file_utils import load_markdown_data, save_markdown_data


class MarkdownRelationStore(RelationStore):
    """Markdown-backed storage for novel-scoped relation graphs."""

    def __init__(self, path_provider: PathProviderLike):
        self.path_provider = path_provider

    def load_relations(self, novel_id: str, default: Any = None) -> Any:
        return load_markdown_data(self.path_provider.relations_file(novel_id), default=default)

    def save_relations(
        self,
        novel_id: str,
        relations: Dict[str, Dict[str, Any]],
        output_path: Optional[str] = None,
    ) -> None:
        if output_path:
            output = Path(output_path)
            path = output if output.suffix.lower() == ".md" else output / f"{novel_id}_relations.md"
        else:
            path = self.path_provider.relations_file(novel_id)

        save_markdown_data(
            path,
            {"novel_id": novel_id, "relations": relations},
            title="RELATION_GRAPH",
            summary=[
                f"- novel_id: {novel_id}",
                f"- relation_count: {len(relations)}",
            ],
        )
