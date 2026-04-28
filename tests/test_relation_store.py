#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path

from src.core.config import Config
from src.core.path_provider import PathProvider
from src.core.relation_store import MarkdownRelationStore
from src.utils.file_utils import load_markdown_data


class RelationStoreTests(unittest.TestCase):
    def test_markdown_relation_store_persists_default_and_explicit_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = Config()
            config.update({"paths": {"relations": str(root / "relations")}})
            store = MarkdownRelationStore(PathProvider(config))
            relations = {
                "刘备_关羽": {
                    "trust": 9,
                    "affection": 8,
                    "power_gap": 0,
                    "conflict_point": "取舍先后",
                }
            }

            store.save_relations("sanguo", relations)
            store.save_relations("sanguo", relations, output_path=str(root / "exports"))

            default_payload = store.load_relations("sanguo", default=None)
            exported_payload = load_markdown_data(root / "exports" / "sanguo_relations.md", default=None)

            self.assertEqual(default_payload["novel_id"], "sanguo")
            self.assertEqual(default_payload["relations"]["刘备_关羽"]["trust"], 9)
            self.assertEqual(exported_payload["relations"]["刘备_关羽"]["affection"], 8)


if __name__ == "__main__":
    unittest.main()
