#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_skill_file(src: Path, dst_root: Path, skill_name: str) -> Path:
    dst = dst_root / skill_name
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src / "SKILL.md", dst / "SKILL.md")
    return dst


def copy_skill_dir(src: Path, dst_root: Path, skill_name: str) -> Path:
    dst = dst_root / skill_name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install Dreamforge adapters for OpenClaw, Hermes Agent, or a local project skills directory"
    )
    parser.add_argument("--openclaw-dir", help="OpenClaw skills root directory")
    parser.add_argument("--hermes-dir", help="Hermes Agent skills root directory")
    parser.add_argument("--skills-dir", help="Generic skills root directory for your own project")
    parser.add_argument(
        "--project-root",
        help="Local project root; installs the generic skill into <project-root>/skills/",
    )
    parser.add_argument(
        "--skill-name",
        default="zaomeng-skill",
        help="Target skill folder name for generic installs (default: zaomeng-skill)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    openclaw_src = repo_root / "openclaw-skill"
    hermes_src = repo_root / "hermes-skill"
    generic_src = repo_root / "skills" / "zaomeng-skill"

    if not openclaw_src.exists() or not hermes_src.exists() or not generic_src.exists():
        raise FileNotFoundError("Missing openclaw-skill/, hermes-skill/, or skills/zaomeng-skill/ directory")

    if not any([args.openclaw_dir, args.hermes_dir, args.skills_dir, args.project_root]):
        print("No target provided. Use --openclaw-dir, --hermes-dir, --skills-dir, or --project-root")
        return 1

    if args.openclaw_dir:
        target = copy_skill_file(openclaw_src, Path(args.openclaw_dir), "zaomeng-skill")
        print(f"Installed OpenClaw skill to: {target}")

    if args.hermes_dir:
        target = copy_skill_file(hermes_src, Path(args.hermes_dir), "zaomeng-skill")
        print(f"Installed Hermes skill to: {target}")

    if args.skills_dir:
        target = copy_skill_dir(generic_src, Path(args.skills_dir), args.skill_name)
        print(f"Installed generic skill to: {target}")

    if args.project_root:
        project_skills_root = Path(args.project_root) / "skills"
        target = copy_skill_dir(generic_src, project_skills_root, args.skill_name)
        print(f"Installed project skill to: {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
