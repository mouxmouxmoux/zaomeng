#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import unittest
from pathlib import Path

from src.core.config import Config
from src.modules.chat_engine import ChatEngine
from src.modules.relationships import RelationshipExtractor
from src.utils.file_utils import save_json


class RelationBehaviorTests(unittest.TestCase):
    def make_config(self, root: Path) -> Config:
        config = Config()
        config.update(
            {
                "paths": {
                    "characters": str(root / "characters"),
                    "relations": str(root / "relations"),
                    "sessions": str(root / "sessions"),
                    "corrections": str(root / "corrections"),
                    "logs": str(root / "logs"),
                }
            }
        )
        for folder in ("characters", "relations", "sessions", "corrections", "logs"):
            (root / folder).mkdir(parents=True, exist_ok=True)
        return config

    def test_extract_pair_interactions_requires_same_sentence(self):
        extractor = RelationshipExtractor(Config())
        chunk = (
            "林黛玉看着贾宝玉，没有说话。"
            "薛宝钗这时才进门。"
            "林黛玉又对贾宝玉说，你该回去了。"
        )
        pairs = extractor._extract_pair_interactions(chunk, ["林黛玉", "贾宝玉", "薛宝钗"])

        self.assertIn("林黛玉_贾宝玉", pairs)
        self.assertEqual(len(pairs["林黛玉_贾宝玉"]), 2)
        self.assertNotIn("林黛玉_薛宝钗", pairs)
        self.assertNotIn("薛宝钗_贾宝玉", pairs)

    def test_chat_engine_scopes_profiles_and_relations_by_novel(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = self.make_config(root)

            save_json(
                root / "characters" / "novel_a" / "林黛玉.json",
                {"name": "林黛玉", "speech_style": "克制", "typical_lines": [], "values": {}},
            )
            save_json(
                root / "characters" / "novel_a" / "贾宝玉.json",
                {"name": "贾宝玉", "speech_style": "直白", "typical_lines": [], "values": {}},
            )
            save_json(
                root / "characters" / "novel_b" / "哈利.json",
                {"name": "哈利", "speech_style": "直接", "typical_lines": [], "values": {}},
            )
            save_json(
                root / "relations" / "novel_a" / "novel_a_relations.json",
                {"林黛玉_贾宝玉": {"trust": 8, "affection": 7, "power_gap": 0}},
            )
            save_json(
                root / "relations" / "novel_b" / "novel_b_relations.json",
                {"哈利_罗恩": {"trust": 2, "affection": 2, "power_gap": 0}},
            )

            engine = ChatEngine(config)
            session = engine.create_session("novel_a.txt", "observe")

            self.assertEqual(session["novel_id"], "novel_a")
            self.assertEqual(session["characters"], ["林黛玉", "贾宝玉"])
            self.assertEqual(session["state"]["relation_matrix"]["林黛玉_贾宝玉"]["trust"], 8)
            self.assertNotIn("哈利", session["characters"])


if __name__ == "__main__":
    unittest.main()
