#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

from src.core.config import Config
from src.modules.chat_engine import ChatEngine
from src.modules.speaker import Speaker


class RelationBehaviorTests(unittest.TestCase):
    def test_target_relation_changes_tone(self):
        speaker = Speaker(Config())
        speaker.reflection.search_similar_corrections = lambda *args, **kwargs: []

        profile = {
            "name": "林黛玉",
            "core_traits": ["敏感", "聪慧"],
            "speech_style": "克制",
            "typical_lines": ["你先把话说清楚。"],
            "values": {"忠诚": 7},
        }
        history = [{"speaker": "贾宝玉", "message": "你别生气。"}]

        hostile_reply = speaker.generate(
            character_profile=profile,
            context="发生争执",
            history=history,
            target_name="薛宝钗",
            relation_state={"affection": 2, "trust": 2, "hostility": 8, "ambiguity": 3},
        )
        warm_reply = speaker.generate(
            character_profile=profile,
            context="发生争执",
            history=history,
            target_name="贾宝玉",
            relation_state={"affection": 9, "trust": 8, "hostility": 1, "ambiguity": 2},
        )

        self.assertIn("保持明显距离", hostile_reply)
        self.assertIn("语气更软", warm_reply)
        self.assertNotEqual(hostile_reply, warm_reply)

    def test_chat_engine_saves_relation_snapshot(self):
        engine = ChatEngine(Config())
        session = {
            "id": "testsession123",
            "state": {
                "relation_matrix": {"A_B": {"trust": 6, "affection": 4, "hostility": 3, "ambiguity": 2}},
                "relation_delta": {"A_B": {"trust": 1}},
            },
        }
        engine._save_session(session)
        snapshot = Path(engine.sessions_dir) / "testsession123_relations.json"
        self.assertTrue(snapshot.exists())


if __name__ == "__main__":
    unittest.main()

