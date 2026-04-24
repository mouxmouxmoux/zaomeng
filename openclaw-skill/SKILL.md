---
name: openclaw-zaomeng
description: OpenClaw adapter for zaomeng local character distillation, relationship extraction, and roleplay chat.
---

# OpenClaw Adapter

Use these CLI commands as the canonical entrypoints:

- `python -m src.core.main distill --novel <path> [--characters A,B] [--force]`
- `python -m src.core.main extract --novel <path> [--output <path>] [--force]`
- `python -m src.core.main chat --novel <path-or-name> --mode observe|act [--character <name>]`
- `python -m src.core.main view --character <name> [--novel <path-or-name>]`
- `python -m src.core.main correct --session <id> --message <raw> --corrected <fixed> [--character <name>]`

## I/O Contract

- Character profiles: `data/characters/<novel_id>/<character>.json`
- Relationship graph: `data/relations/<novel_id>/<novel_id>_relations.json`
- Session data: `data/sessions/<session_id>.json`
- Correction data: `data/corrections/correction_<session>_<ts>.json`

## Runtime Rules

- Require confirmation before high-cost distill/extract runs unless `--force` is present.
- Keep chat turns local-only and compact.
- Apply correction memory before speech generation.
- Preserve UTF-8 JSON outputs with stable keys.
- Do not require cloud LLM or OpenAI API keys.
