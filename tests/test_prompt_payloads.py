#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path

from src.skill_support.prompt_payloads import build_distill_prompt_payload, build_relation_prompt_payload


class PromptPayloadTests(unittest.TestCase):
    def test_build_distill_prompt_payload_contains_prompt_references_and_request(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            novel_path = Path(tmpdir) / "novel.txt"
            novel_path.write_text("甲。乙。丙。", encoding="utf-8")
            payload = build_distill_prompt_payload(
                novel_path,
                characters=["甲", "乙"],
                max_sentences=2,
                max_chars=100,
            )

        self.assertEqual(payload["mode"], "distill")
        self.assertIn("人物档案蒸馏提示词", str(payload["prompt"]))
        self.assertIn("output_schema", payload["references"])
        self.assertEqual(payload["request"]["characters"], ["甲", "乙"])
        self.assertEqual(payload["request"]["excerpt"], "甲。\n乙。")

    def test_build_relation_prompt_payload_contains_excerpt_and_relation_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            novel_path = Path(tmpdir) / "novel.txt"
            novel_path.write_text("宝玉。黛玉。宝钗。", encoding="utf-8")
            payload = build_relation_prompt_payload(
                novel_path,
                max_sentences=2,
                max_chars=100,
            )

        self.assertEqual(payload["mode"], "relation")
        self.assertIn("双人关系抽取提示词", str(payload["prompt"]))
        self.assertEqual(payload["request"]["excerpt"], "宝玉。\n黛玉。")
        self.assertIn("logic_constraint", payload["references"])


if __name__ == "__main__":
    unittest.main()
