#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import copy
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional


@dataclass
class NovelSearchResult:
    index: int
    title: str
    path: str
    url: str = ""
    server_id: str = ""
    size: int = 0
    date_modified: str = ""


def _tool_search(server_id: str, query: str, limit: int, offset: int) -> dict[str, Any]:
    try:
        import sys

        root = Path(__file__).resolve().parents[2]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from hermes_tools import mcp_everything_search_server  # type: ignore

        return mcp_everything_search_server(
            {"server_id": server_id, "query": query, "limit": limit, "offset": offset}
        )
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Everything 搜索失败: {exc}") from exc


def _tool_list_servers() -> dict[str, Any]:
    try:
        import sys

        root = Path(__file__).resolve().parents[2]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from hermes_tools import mcp_everything_list_servers  # type: ignore

        return mcp_everything_list_servers({})
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Everything 服务列表读取失败: {exc}") from exc


def parse_search_results_text(text: str) -> list[NovelSearchResult]:
    results: list[NovelSearchResult] = []
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"^(\d+)\.\s*(.*?)\s*\|\s*(.+)$", line)
        if not match:
            continue
        results.append(
            NovelSearchResult(
                index=int(match.group(1)),
                title=match.group(2).strip(),
                path=match.group(3).strip(),
            )
        )
    return results


def normalize_search_results(payload: Any) -> list[NovelSearchResult]:
    if isinstance(payload, str):
        return parse_search_results_text(payload)
    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        normalized: list[NovelSearchResult] = []
        for idx, item in enumerate(payload["results"], start=1):
            if not isinstance(item, dict):
                continue
            title = str(item.get("name") or item.get("title") or "").strip()
            path = str(item.get("path") or item.get("full_path") or "").strip()
            if not title and path:
                title = Path(path).name
            if title and path:
                normalized.append(
                    NovelSearchResult(
                        index=idx,
                        title=title,
                        path=path,
                        url=str(item.get("url") or "").strip(),
                        server_id=str(payload.get("server", {}).get("id") or item.get("server_id") or "").strip(),
                        size=int(item.get("size") or 0),
                        date_modified=str(item.get("date_modified") or "").strip(),
                    )
                )
        return normalized
    return []


def load_results_from_file(file_path: Optional[str]) -> list[NovelSearchResult]:
    if not file_path:
        return []
    text = Path(file_path).read_text(encoding="utf-8")
    return parse_search_results_text(text)


def search_novel_candidates(
    keyword: str,
    *,
    server_id: str = "",
    limit: int = 10,
    offset: int = 0,
    results_file: Optional[str] = None,
    search_tool: Optional[Any] = None,
    list_servers_tool: Optional[Any] = None,
) -> list[NovelSearchResult]:
    if results_file:
        return load_results_from_file(results_file)

    tool = search_tool or _tool_search
    servers_tool = list_servers_tool or _tool_list_servers
    active_server_id = str(server_id or "").strip()

    if not active_server_id:
        servers_payload = servers_tool()
        servers = []
        if isinstance(servers_payload, dict):
            servers = copy.deepcopy(servers_payload.get("servers") or [])
        if not servers:
            raise RuntimeError("没找到可用的 Everything 服务。")
        active_server_id = str(servers[0].get("id") or "").strip()
        if not active_server_id:
            raise RuntimeError("Everything 服务缺少 server_id。")

    payload = tool(active_server_id, keyword, limit, offset)
    if isinstance(payload, dict) and "server" in payload and isinstance(payload["server"], dict):
        payload = copy.deepcopy(payload)
        payload["server"].setdefault("id", active_server_id)
    return normalize_search_results(payload)


def format_candidate_lines(results: Iterable[NovelSearchResult]) -> list[str]:
    lines: list[str] = []
    for item in results:
        label = item.title or Path(item.path).name or item.path
        lines.append(f"{item.index}. {label} | {item.path}")
    return lines


def shell_render(parts: Iterable[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in parts)


def run_cli_step(parts: list[str], *, workdir: str, dry_run: bool) -> int:
    rendered = shell_render(parts)
    if dry_run:
        print(f"[dry-run] {rendered}")
        return 0
    command = [sys.executable, "-m", "src.core.main", *parts]
    result = subprocess.run(command, cwd=workdir, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"步骤失败: {rendered}")
    return result.returncode
