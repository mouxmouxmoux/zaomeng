---
name: openclaw-dreamforge
description: 小说人物蒸馏、关系提取、群聊模拟的 OpenClaw 适配规则。用于将 distill/chat/view/correct/extract CLI 工作流接入 OpenClaw Agent，基于本地规则引擎输出结构化 JSON、执行成本确认、纠错记忆与会话持久化。
---

# OpenClaw Adapter

## Execute Commands

Use these CLI commands as canonical entrypoints:

- `python -m src.core.main distill --novel <path> [--characters 名1,名2] [--force]`
- `python -m src.core.main extract --novel <path> [--output <path>] [--force]`
- `python -m src.core.main chat --novel <book> --mode observe|act [--character <name>]`
- `python -m src.core.main view --character <name>`
- `python -m src.core.main correct --session <id> --message <raw> --corrected <fixed> [--character <name>]`

## I/O Contract

- Character profile output path: `data/characters/<角色名>.json`
- Relation graph output path: `data/relations/<小说名>_relations.json`
- Session output path: `data/sessions/<session_id>.json`
- Correction output path: `data/corrections/correction_<session>_<ts>.json`

## Runtime Rules

- Require user confirmation before high-cost distillation/extraction unless `--force` is passed.
- Keep per-turn context compact in chat mode.
- Apply correction memory before generating character speech.
- Preserve UTF-8 JSON outputs with stable key names.
- Do not require cloud LLM or OpenAI API key.
