# zaomeng.skill

[中文](README.md) | [English](README.en.md)

`zaomeng` is a local novel-character toolkit.

It does three things:

- distills characters from a novel
- extracts character relationships
- lets those characters enter group chat or roleplay after distillation

It is not a generic chatbot.  
It is closer to a character engine for fiction.

## Read This First

The correct order is not “start chatting immediately.”  
**Step one is always: provide the novel first, then distill the characters. Only after distillation should you enter chat or roleplay.**

The most common user flow is:

1. attach a novel file, or provide the novel file path
2. say which characters you want distilled
3. after distillation finishes, enter group chat or roleplay

## One Complete Example

### Step 1: provide the novel, then ask for distillation

For example, after providing *Dream of the Red Chamber*, you say:

```text
Distill Lin Daiyu and Jia Baoyu for me
```

The system will first process the novel and build character profiles plus relationship data.

### Step 2: only after distillation, enter chat

Then you say:

```text
Let me play Jia Baoyu and chat with Lin Daiyu
```

Only now does the system enter the flow where you play Baoyu and Daiyu replies.

Then you continue with:

```text
Sister, are you feeling well today?
```

The system treats that as Baoyu's actual line and lets Daiyu answer.

### Step 3: multi-character chat also comes after distillation

For example, after providing *Romance of the Three Kingdoms* and distilling Liu Bei, Zhang Fei, and Guan Yu, you say:

```text
Enter Liu Bei, Zhang Fei, Guan Yu group chat mode
```

Then you continue with:

```text
Liu Bei: Brothers, now that the fighting has briefly eased, this is a rare moment of calm.
```

Now the system lets Zhang Fei and Guan Yu respond.

## Things You Can Say Directly

### Distill characters

```text
Distill Lin Daiyu and Jia Baoyu for me
```

```text
Extract character personas for Liu Bei, Zhang Fei, and Guan Yu from this novel
```

```text
Distill Baoyu and Daiyu from Dream of the Red Chamber
```

### Enter roleplay after distillation

```text
Let me play Jia Baoyu and chat with Lin Daiyu
```

```text
I'll play Liu Bei. Let Guan Yu and Zhang Fei reply to me
```

### Enter group chat after distillation

```text
Enter Liu Bei, Zhang Fei, Guan Yu group chat mode
```

```text
Let Baoyu, Daiyu, and Baochai discuss this together
```

### Make everyone speak immediately

```text
Let everyone say one line about the alliance with Sun Quan
```

```text
Scene: Daiyu arrives at the Jia household. Let the relevant characters begin naturally
```

## What It Can Do

### 1. Character distillation

Extract major characters from `.txt` or `.epub` novels and build profiles including:

- `core_traits`
- `values`
- `speech_style`
- `typical_lines`
- `decision_rules`
- `identity_anchor`
- `soul_goal`
- `life_experience`
- `taboo_topics`
- `forbidden_behaviors`

### 2. Relationship extraction

Build a relationship graph from the novel. Current core fields include:

- `trust`
- `affection`
- `power_gap`
- `conflict_point`
- `typical_interaction`

### 3. Character chat

Two chat styles are supported:

- `observe`
  You provide a scene, topic, or opening line and let characters interact naturally
- `act`
  You control one character directly while others reply in character

### 4. Correction memory

If a line is clearly out of character, you can save a correction.  
Later conversations will try to avoid the same kind of mistake.

### 5. Markdown persona bundle

Character storage is now markdown-first rather than legacy JSON-first.

Each character lives under:

- `data/characters/<novel_id>/<character>/PROFILE.md`
- `data/characters/<novel_id>/<character>/NAVIGATION.md`
- `data/characters/<novel_id>/<character>/SOUL.md`
- `data/characters/<novel_id>/<character>/IDENTITY.md`
- `data/characters/<novel_id>/<character>/AGENTS.md`
- `data/characters/<novel_id>/<character>/MEMORY.md`
- `data/characters/<novel_id>/<character>/RELATIONS.md`

## Quick Start

### 1. Prepare a novel file

Supported formats:

- `.txt`
- `.epub`

### 2. Distill first, then chat

Using *Dream of the Red Chamber* as an example:

```bash
python -m src.core.main distill --novel data/hongloumeng.txt --characters 林黛玉,贾宝玉 --force
python -m src.core.main extract --novel data/hongloumeng.txt --force
```

This creates:

- `data/characters/hongloumeng/<character>/`
- `data/relations/hongloumeng/hongloumeng_relations.md`

### 3. After distillation, start chatting

Recommended natural-language flow:

```bash
python -m src.core.main chat --novel data/hongloumeng.txt --mode auto --message "让我扮演贾宝玉和林黛玉聊天"
```

Then continue with:

```bash
python -m src.core.main chat --novel data/hongloumeng.txt --session <session_id> --message "妹妹今日可大安了？"
```

If you want a multi-character group chat:

```bash
python -m src.core.main chat --novel data/sanguo.txt --mode auto --message "进入刘备、张飞、关羽群聊模式"
python -m src.core.main chat --novel data/sanguo.txt --session <session_id> --message "刘备：二位贤弟，近日战事稍歇。"
```

## Other Commands

### View a character profile

```bash
python -m src.core.main view --character 林黛玉 --novel data/hongloumeng.txt
```

### Save a correction

```bash
python -m src.core.main correct \
  --session <session_id> \
  --message "Baoyu plans to leave home and become a merchant" \
  --corrected "Baoyu has long disliked worldly ambition and would rather remain among poetry, gardens, and intimate company" \
  --character 贾宝玉
```

## Command Overview

```bash
python -m src.core.main distill --novel <path> [--characters A,B] [--output <dir>] [--force]
python -m src.core.main extract --novel <path> [--output <path>] [--force]
python -m src.core.main chat --novel <path-or-name> --mode auto|observe|act [--character <name>] [--session <id>] [--message <text>]
python -m src.core.main view --character <name> [--novel <path-or-name>]
python -m src.core.main correct --session <id> --message <raw> --corrected <fixed> [--character <name>] [--target <name>] [--reason <text>]
```

## Project Structure

```text
src/core/main.py
src/modules/distillation.py
src/modules/relationships.py
src/modules/chat_engine.py
src/modules/reflection.py
src/modules/speaker.py
src/utils/
openclaw-skill/
hermes-skill/
skills/zaomeng-skill/
clawhub-zaomeng-skill/
tests/test_relation_behavior.py
```
