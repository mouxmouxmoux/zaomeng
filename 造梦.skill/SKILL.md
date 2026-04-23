---
name: zaomeng-skill
description: 本地无模型依赖的小说角色蒸馏与群聊 skill。用于 OpenClaw/Hermes Agent 安装后执行 distill/chat/view/correct/extract 命令，输出角色档案、关系网、会话记录与纠错库。
---

# 造梦.skill

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

## Install

- OpenClaw: copy [openclaw-skill/SKILL.md](d:\work2\Dreamforge\openclaw-skill\SKILL.md) to `<openclaw-skills-root>/zaomeng-skill/SKILL.md`
- Hermes: copy [hermes-skill/SKILL.md](d:\work2\Dreamforge\hermes-skill\SKILL.md) to `<hermes-skills-root>/zaomeng-skill/SKILL.md`
- Or run:
  `py scripts/install_skill.py --openclaw-dir <openclaw-skills-root> --hermes-dir <hermes-skills-root>`

