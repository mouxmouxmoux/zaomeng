#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any, Dict

from src.core.contracts import RelationVisualizationExporter
from src.utils.file_utils import save_markdown_data


class MermaidRelationVisualizationExporter(RelationVisualizationExporter):
    """Export relation visuals through the existing extractor rendering helpers."""

    def __init__(self, renderer: Any):
        self.renderer = renderer

    def export_visualizations(self, relations: Dict[str, Dict[str, Any]], novel_id: str) -> None:
        node_styles = self.renderer._build_visual_node_styles(novel_id, relations)
        mermaid_graph = self.renderer._render_mermaid_graph(relations, node_styles=node_styles)
        mermaid_path = self.renderer.path_provider.visualization_file(novel_id, ".mermaid.md")
        save_markdown_data(
            mermaid_path,
            {
                "novel_id": novel_id,
                "relation_count": len(relations),
                "diagram": mermaid_graph,
            },
            title="RELATION_GRAPH_VISUAL",
            summary=[
                f"- novel_id: {novel_id}",
                f"- relation_count: {len(relations)}",
            ],
        )

        html_path = self.renderer.path_provider.visualization_file(novel_id, ".html")
        html_path.write_text(
            self.renderer._render_relation_html(
                novel_id,
                relations,
                node_styles=node_styles,
                mermaid_graph=mermaid_graph,
            ),
            encoding="utf-8",
        )
