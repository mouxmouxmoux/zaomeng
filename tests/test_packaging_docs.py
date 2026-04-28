#!/usr/bin/env python3

import unittest
from pathlib import Path

from scripts.check_runtime_mirror import (
    load_documented_runtime_wrapper_paths,
    load_documented_shared_runtime_core_paths,
    load_managed_runtime_paths,
)


class PackagingDocsTests(unittest.TestCase):
    def test_manifest_mentions_shared_runtime_core_modules(self):
        manifest_text = Path("clawhub-zaomeng-skill/MANIFEST.md").read_text(encoding="utf-8")
        for entry in load_documented_shared_runtime_core_paths():
            self.assertIn(entry, manifest_text)

    def test_install_and_skill_docs_describe_wrapper_split(self):
        install_text = Path("clawhub-zaomeng-skill/INSTALL.md").read_text(encoding="utf-8")
        skill_text = Path("clawhub-zaomeng-skill/SKILL.md").read_text(encoding="utf-8")
        for entry in load_documented_runtime_wrapper_paths():
            self.assertIn(entry, install_text)
            self.assertIn(entry, skill_text)
        for entry in load_documented_shared_runtime_core_paths():
            self.assertIn(entry, install_text)
            self.assertIn(entry, skill_text)

    def test_readmes_describe_shared_and_wrapper_runtime_layers(self):
        root_readme_en = Path("README.en.md").read_text(encoding="utf-8")
        skill_readme = Path("clawhub-zaomeng-skill/README.md").read_text(encoding="utf-8")
        skill_readme_en = Path("clawhub-zaomeng-skill/README_EN.md").read_text(encoding="utf-8")

        self.assertIn("src/core/runtime_parts.py", root_readme_en)
        self.assertIn("src/core/logging_utils.py", root_readme_en)
        for entry in load_documented_runtime_wrapper_paths():
            self.assertIn(entry, skill_readme)
            self.assertIn(entry, skill_readme_en)
        for entry in load_documented_shared_runtime_core_paths():
            self.assertIn(entry, skill_readme)
            self.assertIn(entry, skill_readme_en)

    def test_manifest_lists_all_managed_runtime_python_files(self):
        manifest_text = Path("clawhub-zaomeng-skill/MANIFEST.md").read_text(encoding="utf-8")
        for entry in load_managed_runtime_paths():
            self.assertIn(entry, manifest_text)


if __name__ == "__main__":
    unittest.main()
