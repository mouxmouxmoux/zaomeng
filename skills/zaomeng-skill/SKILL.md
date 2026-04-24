---
name: zaomeng-skill
description: Dreamforge local skill for character distillation, relationship extraction, and roleplay chat workflows.
---

# Zaomeng Skill

Use this skill to run Dreamforge's local workflow without cloud model dependencies.

## Commands

- `python -m src.core.main distill --novel <path> [--characters A,B] [--force]`
- `python -m src.core.main extract --novel <path> [--output <path>] [--force]`
- `python -m src.core.main chat --novel <path-or-name> --mode observe|act [--character <name>]`
- `python -m src.core.main view --character <name> [--novel <path-or-name>]`
- `python -m src.core.main correct --session <id> --message <raw> --corrected <fixed> [--character <name>]`

## Data Paths

- `data/characters/<novel_id>/`
- `data/relations/<novel_id>/`
- `data/sessions/`
- `data/corrections/`

## Notes

- The workflow is local-first and does not require OpenAI API access.
- The host project only needs Python plus this repository's CLI entrypoints.
