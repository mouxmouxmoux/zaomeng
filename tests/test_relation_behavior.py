#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import unittest
from pathlib import Path

from src.core.config import Config
from src.modules.chat_engine import ChatEngine
from src.modules.distillation import NovelDistiller
from src.modules.relationships import RelationshipExtractor
from src.utils.file_utils import load_json, save_json


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

    def test_distill_with_explicit_characters_uses_two_char_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = self.make_config(root)
            novel_path = root / "honglou.txt"
            novel_path.write_text(
                "\u9edb\u7389\u770b\u7740\u5b9d\u7389\uff0c\u6ca1\u6709\u8bf4\u8bdd\u3002"
                "\u5b9d\u7389\u7b11\u9053\uff1a\u201c\u4f60\u53c8\u60f3\u591a\u4e86\u3002\u201d"
                "\u9edb\u7389\u5fc3\u91cc\u4e00\u9178\uff0c\u5374\u8fd8\u662f\u770b\u7740\u4ed6\u3002",
                encoding="utf-8",
            )

            distiller = NovelDistiller(config)
            result = distiller.distill(
                str(novel_path),
                characters=["\u6797\u9edb\u7389", "\u8d3e\u5b9d\u7389"],
            )

            self.assertGreater(result["\u6797\u9edb\u7389"]["evidence"]["description_count"], 0)
            self.assertGreater(result["\u8d3e\u5b9d\u7389"]["evidence"]["dialogue_count"], 0)

    def test_relationship_extractor_matches_two_char_aliases(self):
        extractor = RelationshipExtractor(Config())
        alias_map = {
            "\u6797\u9edb\u7389": ["\u6797\u9edb\u7389", "\u9edb\u7389"],
            "\u8d3e\u5b9d\u7389": ["\u8d3e\u5b9d\u7389", "\u5b9d\u7389"],
            "\u859b\u5b9d\u9497": ["\u859b\u5b9d\u9497", "\u5b9d\u9497"],
        }
        chunk = (
            "\u9edb\u7389\u770b\u7740\u5b9d\u7389\uff0c\u6ca1\u6709\u8bf4\u8bdd\u3002"
            "\u5b9d\u9497\u8fd9\u65f6\u624d\u8fdb\u95e8\u3002"
            "\u9edb\u7389\u53c8\u5bf9\u5b9d\u7389\u8bf4\uff0c\u4f60\u8be5\u56de\u53bb\u4e86\u3002"
        )

        pairs = extractor._extract_pair_interactions(
            chunk,
            ["\u6797\u9edb\u7389", "\u8d3e\u5b9d\u7389", "\u859b\u5b9d\u9497"],
            alias_map=alias_map,
        )

        self.assertIn("\u6797\u9edb\u7389_\u8d3e\u5b9d\u7389", pairs)
        self.assertEqual(len(pairs["\u6797\u9edb\u7389_\u8d3e\u5b9d\u7389"]), 2)
        self.assertNotIn("\u6797\u9edb\u7389_\u859b\u5b9d\u9497", pairs)
        self.assertNotIn("\u859b\u5b9d\u9497_\u8d3e\u5b9d\u7389", pairs)

    def test_act_mode_prefers_explicit_or_strongest_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = self.make_config(root)

            save_json(
                root / "characters" / "hongloumeng" / "林黛玉.json",
                {"name": "林黛玉", "speech_style": "克制", "typical_lines": [], "values": {}},
            )
            save_json(
                root / "characters" / "hongloumeng" / "贾宝玉.json",
                {"name": "贾宝玉", "speech_style": "直白", "typical_lines": [], "values": {}},
            )
            save_json(
                root / "characters" / "hongloumeng" / "冯紫英.json",
                {"name": "冯紫英", "speech_style": "直白", "typical_lines": [], "values": {}},
            )
            save_json(
                root / "relations" / "hongloumeng" / "hongloumeng_relations.json",
                {
                    "林黛玉_贾宝玉": {"trust": 9, "affection": 9, "power_gap": 0},
                    "冯紫英_贾宝玉": {"trust": 4, "affection": 3, "power_gap": 0},
                },
            )

            engine = ChatEngine(config)
            session = engine.create_session("hongloumeng.txt", "act")

            responders = engine._active_characters(session, speaker="贾宝玉", context="妹妹今日可大安了？")
            self.assertEqual(responders, ["林黛玉"])

            explicit = engine._active_characters(session, speaker="贾宝玉", context="林妹妹今日可大安了？")
            self.assertEqual(explicit, ["林黛玉"])

    def test_save_json_replaces_surrogates(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "session.json"
            save_json(target, {"message": "x\udce5y"})
            payload = load_json(target)
            self.assertEqual(payload["message"], "x?y")

    def test_distiller_rejects_name_plus_dialogue_verb_noise(self):
        distiller = NovelDistiller(Config())
        self.assertFalse(distiller._looks_like_name("凤姐笑"))
        self.assertFalse(distiller._looks_like_name("凤姐听"))
        self.assertTrue(distiller._looks_like_name("贾宝玉"))

    def test_chat_engine_normalizes_legacy_noisy_profile_and_relation_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = self.make_config(root)

            save_json(
                root / "characters" / "hongloumeng" / "凤姐笑.json",
                {"name": "凤姐笑", "speech_style": "凌厉", "typical_lines": [], "values": {}},
            )
            save_json(
                root / "characters" / "hongloumeng" / "贾宝玉.json",
                {"name": "贾宝玉", "speech_style": "直白", "typical_lines": [], "values": {}},
            )
            save_json(
                root / "relations" / "hongloumeng" / "hongloumeng_relations.json",
                {"凤姐听_贾宝玉": {"trust": 6, "affection": 4, "power_gap": 0}},
            )

            engine = ChatEngine(config)
            session = engine.create_session("hongloumeng.txt", "act")

            self.assertIn("凤姐", session["characters"])
            self.assertNotIn("凤姐笑", session["characters"])
            self.assertEqual(session["state"]["relation_matrix"]["凤姐_贾宝玉"]["trust"], 6)


if __name__ == "__main__":
    unittest.main()
