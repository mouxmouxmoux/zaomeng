#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_skill(src: Path, dst_root: Path, skill_name: str) -> Path:
    dst = dst_root / skill_name
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src / "SKILL.md", dst / "SKILL.md")
    return dst


def main() -> int:
    parser = argparse.ArgumentParser(description="Install 造梦.skill adapters for OpenClaw and Hermes Agent")
    parser.add_argument("--openclaw-dir", help="OpenClaw skills root directory")
    parser.add_argument("--hermes-dir", help="Hermes Agent skills root directory")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    openclaw_src = repo_root / "openclaw-skill"
    hermes_src = repo_root / "hermes-skill"

    if not openclaw_src.exists() or not hermes_src.exists():
        raise FileNotFoundError("Missing openclaw-skill/ or hermes-skill/ directory")

    if not args.openclaw_dir and not args.hermes_dir:
        print("No target provided. Use --openclaw-dir and/or --hermes-dir")
        return 1

    if args.openclaw_dir:
        target = copy_skill(openclaw_src, Path(args.openclaw_dir), "zaomeng-skill")
        print(f"Installed OpenClaw skill to: {target}")

    if args.hermes_dir:
        target = copy_skill(hermes_src, Path(args.hermes_dir), "zaomeng-skill")
        print(f"Installed Hermes skill to: {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

