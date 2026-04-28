#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path

from src.core.config import Config
from src.core.path_provider import PathProvider
from src.core.session_store import MarkdownSessionStore
from src.utils.file_utils import load_markdown_data


class SessionStoreTests(unittest.TestCase):
    def test_markdown_session_store_persists_session_and_relation_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = Config()
            config.update({"paths": {"sessions": str(root / "sessions")}})
            store = MarkdownSessionStore(PathProvider(config))
            session = {
                "id": "abc123",
                "novel_id": "sanguo",
                "mode": "observe",
                "updated_at": 1234567890,
                "characters": ["刘备", "关羽"],
                "state": {
                    "relation_matrix": {"关羽_刘备": {"trust": 9}},
                    "relation_delta": {"关羽_刘备": {"trust": 10}},
                },
            }

            store.save_session(session)
            store.save_relation_snapshot(session)

            loaded_session = store.load_session("abc123", default=None)
            loaded_snapshot = load_markdown_data(root / "sessions" / "abc123_relations.md", default=None)

            self.assertEqual(loaded_session["id"], "abc123")
            self.assertEqual(loaded_session["novel_id"], "sanguo")
            self.assertEqual(loaded_snapshot["session_id"], "abc123")
            self.assertEqual(loaded_snapshot["relation_matrix"]["关羽_刘备"]["trust"], 9)
            self.assertEqual(loaded_snapshot["relation_delta"]["关羽_刘备"]["trust"], 10)


if __name__ == "__main__":
    unittest.main()
