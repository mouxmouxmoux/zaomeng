#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any, Dict

from src.core.contracts import PathProviderLike, SessionStore
from src.utils.file_utils import load_markdown_data, save_markdown_data


class MarkdownSessionStore(SessionStore):
    """Markdown-backed session persistence for chat runtime state."""

    def __init__(self, path_provider: PathProviderLike):
        self.path_provider = path_provider

    def load_session(self, session_id: str, default: Any = None) -> Any:
        return load_markdown_data(self._session_path(session_id), default=default)

    def save_session(self, session: Dict[str, Any]) -> None:
        save_markdown_data(
            self._session_path(str(session.get("id", ""))),
            session,
            title="SESSION",
            summary=[
                f"- id: {session.get('id', '')}",
                f"- novel_id: {session.get('novel_id', '')}",
                f"- mode: {session.get('mode', '')}",
            ],
        )

    def save_relation_snapshot(self, session: Dict[str, Any]) -> None:
        payload = {
            "session_id": session.get("id"),
            "novel_id": session.get("novel_id"),
            "updated_at": session.get("updated_at"),
            "relation_matrix": session.get("state", {}).get("relation_matrix", {}),
            "relation_delta": session.get("state", {}).get("relation_delta", {}),
        }
        save_markdown_data(
            self._relation_snapshot_path(str(session.get("id", ""))),
            payload,
            title="SESSION_RELATIONS",
            summary=[
                f"- session_id: {session.get('id', '')}",
                f"- novel_id: {session.get('novel_id', '')}",
            ],
        )

    def _session_path(self, session_id: str):
        return self.path_provider.sessions_dir() / f"{session_id}.md"

    def _relation_snapshot_path(self, session_id: str):
        return self.path_provider.sessions_dir() / f"{session_id}_relations.md"
