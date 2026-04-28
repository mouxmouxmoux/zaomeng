#!/usr/bin/env python3

import unittest
from pathlib import Path

from scripts.check_runtime_mirror import load_runtime_owned_patterns


class RuntimeWrapperTests(unittest.TestCase):
    EXPECTED_IMPORTS = {
        "core/main.py": "from src.core.cli_app import ChatIntent, ZaomengCLI as _SharedZaomengCLI",
        "core/runtime_factory.py": "from src.core.runtime_parts import RuntimeDependencyOverrides, RuntimeParts, build_runtime_parts",
        "core/logging_utils.py": "from src.core.logging_setup import setup_logging",
    }

    def test_runtime_owned_wrappers_delegate_to_shared_modules(self):
        for relative_path in load_runtime_owned_patterns():
            source_path = Path("src") / Path(relative_path)
            runtime_path = Path("clawhub-zaomeng-skill/runtime/src") / Path(relative_path)
            expected_import = self.EXPECTED_IMPORTS[relative_path]

            for path in (source_path, runtime_path):
                text = path.read_text(encoding="utf-8")
                self.assertIn(expected_import, text, msg=f"Expected shared delegation in {path}")
                self.assertLessEqual(len(text.splitlines()), 40, msg=f"Wrapper grew too large: {path}")

    def test_runtime_owned_wrappers_match_between_source_and_runtime(self):
        for relative_path in load_runtime_owned_patterns():
            source_path = Path("src") / Path(relative_path)
            runtime_path = Path("clawhub-zaomeng-skill/runtime/src") / Path(relative_path)
            source_text = source_path.read_text(encoding="utf-8").replace("\r\n", "\n")
            runtime_text = runtime_path.read_text(encoding="utf-8").replace("\r\n", "\n")
            self.assertEqual(source_text, runtime_text, msg=f"Wrapper drift detected for {relative_path}")


if __name__ == "__main__":
    unittest.main()
