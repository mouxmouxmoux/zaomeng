#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.config import Config
from src.core.llm_client import LLMClient
from src.modules.reflection import ReflectionEngine
from src.modules.speaker import Speaker
from src.utils.file_utils import ensure_dir, load_json, save_json


class ChatEngine:
    """Multi-character chat with observe/act modes and inline commands."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.llm = LLMClient(self.config)
        self.reflection = ReflectionEngine(self.config)
        self.speaker = Speaker(self.config)
        self.characters_dir = Path(self.config.get_path("characters"))
        self.sessions_dir = ensure_dir(self.config.get_path("sessions"))
        self.relations_dir = ensure_dir(self.config.get_path("relations"))

    def create_session(self, novel: str, mode: str) -> Dict[str, Any]:
        profiles = self._load_character_profiles()
        if not profiles:
            raise RuntimeError("未找到角色档案，请先运行 distill。")
        session = {
            "id": uuid.uuid4().hex[:12],
            "title": f"{novel}_{mode}_{int(time.time())}",
            "novel": novel,
            "mode": mode,
            "created_at": int(time.time()),
            "characters": list(profiles.keys()),
            "history": [],
            "state": {"emotion": {}, "relation_delta": {}},
        }
        self._save_session(session)
        return session

    def restore_session(self, session_id: str) -> Dict[str, Any]:
        path = self.sessions_dir / f"{session_id}.json"
        data = load_json(path, default=None)
        if not data:
            raise FileNotFoundError(f"会话不存在: {session_id}")
        return data

    def observe_mode(self, session: Dict[str, Any]) -> None:
        print("进入 observe 模式。输入 /save /reflect /correct /quit")
        while True:
            user_msg = input("\n你: ").strip()
            if not user_msg:
                continue
            if self._handle_inline_command(session, user_msg):
                if user_msg == "/quit":
                    break
                continue

            session["history"].append({"speaker": "旁白", "message": user_msg, "ts": int(time.time())})
            profiles = self._load_character_profiles()
            for name in session["characters"][:4]:
                profile = profiles.get(name, {"name": name})
                reply = self.speaker.generate(
                    character_profile=profile,
                    context=user_msg,
                    history=session["history"],
                    relation_hint=self._relation_hint(name, session["characters"]),
                )
                checked = self.reflection.detect_ooc(profile, reply)
                if checked.is_ooc and checked.reasons:
                    reply = f"{reply}（自检修正）"
                print(f"{name}: {reply}")
                session["history"].append({"speaker": name, "message": reply, "ts": int(time.time())})

            self._update_state(session)
            self._save_session(session)
            self._print_turn_cost()

    def act_mode(self, session: Dict[str, Any], character: str) -> None:
        print(f"进入 act 模式，你扮演 {character}。输入 /save /reflect /correct /quit")
        while True:
            user_msg = input(f"\n{character}(你): ").strip()
            if not user_msg:
                continue
            if self._handle_inline_command(session, user_msg):
                if user_msg == "/quit":
                    break
                continue

            session["history"].append({"speaker": character, "message": user_msg, "ts": int(time.time())})
            profiles = self._load_character_profiles()
            for name in session["characters"][:4]:
                if name == character:
                    continue
                profile = profiles.get(name, {"name": name})
                reply = self.speaker.generate(
                    character_profile=profile,
                    context=user_msg,
                    history=session["history"],
                    relation_hint=self._relation_hint(name, session["characters"]),
                )
                checked = self.reflection.detect_ooc(profile, reply)
                if checked.is_ooc and checked.reasons:
                    reply = f"{reply}（根据人设收束）"
                print(f"{name}: {reply}")
                session["history"].append({"speaker": name, "message": reply, "ts": int(time.time())})

            self._update_state(session)
            self._save_session(session)
            self._print_turn_cost()

    def _handle_inline_command(self, session: Dict[str, Any], command: str) -> bool:
        if command == "/quit":
            self._save_session(session)
            print("会话结束。")
            return True
        if command == "/save":
            self._save_session(session)
            print(f"已保存会话: {session['id']}")
            return True
        if command == "/reflect":
            self._reflect_last_turn(session)
            return True
        if command.startswith("/correct"):
            # /correct 角色|原句|修正句
            payload = command[len("/correct") :].strip()
            parts = [p.strip() for p in payload.split("|")]
            if len(parts) != 3:
                print("格式错误。用法: /correct 角色|原句|修正句")
                return True
            item = self.reflection.save_correction(
                session_id=session["id"],
                character=parts[0],
                original_message=parts[1],
                corrected_message=parts[2],
                reason="inline_command",
            )
            print(f"纠错已记录: {item['character']}")
            return True
        return False

    def _reflect_last_turn(self, session: Dict[str, Any]) -> None:
        if not session["history"]:
            print("无历史可反思。")
            return
        profiles = self._load_character_profiles()
        last = session["history"][-1]
        profile = profiles.get(last["speaker"])
        if not profile:
            print("最近一条不是角色发言。")
            return
        check = self.reflection.detect_ooc(profile, last["message"])
        if not check.is_ooc:
            print("反思结果：最近发言符合人设。")
            return
        print("反思结果：疑似 OOC")
        for reason in check.reasons:
            print(f"- {reason}")

    def _relation_hint(self, speaker: str, all_chars: List[str]) -> str:
        rel_file = self._latest_relations_file()
        if not rel_file:
            return ""
        rel = load_json(rel_file, default={})
        hints = []
        for other in all_chars:
            if other == speaker:
                continue
            key = "_".join(sorted([speaker, other]))
            if key in rel:
                item = rel[key]
                hints.append(f"{other}(trust={item.get('trust',5)},aff={item.get('affection',5)})")
        return "; ".join(hints[:3])

    def _latest_relations_file(self) -> Optional[Path]:
        files = sorted(self.relations_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        return files[0] if files else None

    def _update_state(self, session: Dict[str, Any]) -> None:
        latest = session["history"][-6:]
        emotion = session["state"]["emotion"]
        for item in latest:
            speaker = item["speaker"]
            if speaker in ("旁白", "用户"):
                continue
            delta = 0
            msg = item["message"]
            if any(k in msg for k in ("！", "愤怒", "生气", "质问")):
                delta += 1
            if any(k in msg for k in ("冷静", "平静", "慢慢说", "理解")):
                delta -= 1
            emotion[speaker] = max(-5, min(5, emotion.get(speaker, 0) + delta))

    def _print_turn_cost(self) -> None:
        summary = self.llm.get_cost_summary()
        print(
            f"[本轮后累计] token={summary['total_tokens']} "
            f"session=${summary['session_cost']:.4f} daily=${summary['daily_cost']:.4f}"
        )

    def _save_session(self, session: Dict[str, Any]) -> None:
        save_json(self.sessions_dir / f"{session['id']}.json", session)

    def _load_character_profiles(self) -> Dict[str, Dict[str, Any]]:
        profiles: Dict[str, Dict[str, Any]] = {}
        if not self.characters_dir.exists():
            return profiles
        for file in self.characters_dir.glob("*.json"):
            item = load_json(file, default=None)
            if item and isinstance(item, dict) and item.get("name"):
                profiles[item["name"]] = item
        return profiles

