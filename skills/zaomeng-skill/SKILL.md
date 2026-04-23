---
name: zaomeng-skill
description: 本地规则引擎的小说角色蒸馏与群聊能力。用于执行 distill/chat/view/correct/extract 工作流，产出角色档案、关系网、会话与纠错 JSON；适合 OpenClaw 与通用 Agent Skills 生态安装。
---

# Zaomeng Skill

Use this skill to run Dreamforge's local, no-cloud-model workflow.

## Commands

- `py -m src.core.main distill --novel <path> [--characters 名1,名2] [--force]`
- `py -m src.core.main extract --novel <path> [--output <path>] [--force]`
- `py -m src.core.main chat --novel <book> --mode observe|act [--character <name>]`
- `py -m src.core.main view --character <name>`
- `py -m src.core.main correct --session <id> --message <raw> --corrected <fixed> [--character <name>]`

## Data Paths

- `data/characters/`
- `data/relations/`
- `data/sessions/`
- `data/corrections/`

## Notes

- This skill is local-first and does not require OpenAI API.
- It relies on Python runtime and project files in this repository.

