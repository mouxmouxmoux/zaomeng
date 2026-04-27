# zaomeng.skill

[中文](README.md) | [English](README.en.md)

Local toolkit for turning novels into reusable, constrained character assets:

- character distillation
- relationship extraction
- constrained roleplay chat
- correction memory
- agent integration for OpenClaw, Hermes, ClawHub, and similar tools

This is not a generic chatbot. The goal is to make characters behave like themselves, not like a generic assistant wearing a costume.

## Read This First: Natural Language Is The Primary Interface

If you are integrating `zaomeng` through OpenClaw, Hermes, ClawHub, or another agent layer, the recommended approach is:

- pass the user's raw request into `chat --mode auto`
- let `zaomeng` decide whether the request is a mode switch or an actual spoken line
- avoid manually simulating the scene outside the engine

Recommended mental model:

- if the user is describing a play pattern, that is a **mode-intent request**
- if the user is speaking as a character, that is an **in-character line**
- `zaomeng` should map the first case to mode setup and the second case to turn execution

### Natural Language To Mode Mapping

Requests like these should usually mean **enter `act` mode**:

- `Let me play Jia Baoyu and chat with Lin Daiyu`
- `I'll play Jia Baoyu, you make Lin Daiyu reply to me`
- `I say one line, Daiyu answers one line`
- `Enter Bao-Dai act mode`
- `I want to play Liu Bei`

These are setup requests, not spoken dialogue lines.

Expected behavior:

1. create or resume an `act` session
2. remember which role the user controls
3. wait for the user's next actual line before generating the other character's reply

Requests like these should usually mean **enter `observe` mode**:

- `Enter Liu Bei, Zhang Fei, Guan Yu group chat mode`
- `Start a Bao-Dai group chat`
- `Switch to observe mode`

Requests like these should mean **run one real `observe` turn immediately**, not just switch modes:

- `Let everyone say one line about this matter`
- `Scene: Daiyu arrives at the Jia household. Let the relevant characters begin naturally`
- `Have everyone react to the alliance with Sun Quan`

### One Rule For Agent Builders

If the user sounds like they are describing the gameplay, switch mode first.  
If the user sounds like they are already speaking in character, run the line.

### What OpenClaw / Hermes Style Tools Should Do

- keep the user's original wording whenever possible
- default to `chat --mode auto`
- do not rewrite setup requests into freeform scene demos
- do not answer `Let me play Baoyu and chat with Daiyu` with `Sure, here's a simulated Bao-Dai interaction...`

Natural language intent should be the first-class entry point. CLI is the execution layer underneath.

## Typical Natural Language Flows

### 1. User wants one-to-one act mode

User says:

```text
让我扮演贾宝玉和林黛玉聊天
```

Expected behavior:

- enter `act`
- set `贾宝玉` as the controlled role
- prioritize `林黛玉` as the reply target
- return a resumable session

Then the user says:

```text
妹妹今日可大安了？
```

Only now should this be treated as Baoyu's actual line.

### 2. User wants multi-character observe mode

User says:

```text
进入刘备、张飞、关羽群聊模式
```

Expected behavior:

- enter `observe`
- scope the session to those characters
- wait for the next scene prompt or opening line

Then the user says:

```text
刘备：二位贤弟，近日战事稍歇，倒是难得清闲。
```

Now Zhang Fei and Guan Yu should respond in character.

### 3. User wants everyone to speak right away

User says:

```text
请让大家围绕联合孙权这件事各说一句
```

Expected behavior:

- treat it as a real `observe` turn
- do not only reply with `observe mode activated`
- generate the character replies immediately

## Core Capabilities

### 1. Character Distillation

Extract major characters from `.txt` or `.epub` novels and build persona-rich profiles, including:

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

### 2. Relationship Extraction

Build a relationship graph from the novel. Current core fields include:

- `trust`
- `affection`
- `power_gap`
- `conflict_point`
- `typical_interaction`

### 3. Roleplay Chat

Two supported modes:

- `observe`
  You provide a scene or prompt and the characters interact around it.
- `act`
  You control one character and the others reply based on persona and relationship state.

Chat supports:

- `/save`
- `/reflect`
- `/correct character|target|original|corrected|reason`
- `/quit`

### 4. Correction Memory

If a line is clearly out of character, you can save a correction and later runs will try to avoid the same mistake.

### 5. Markdown Persona Bundle

Character storage is now markdown-first, not legacy JSON-first.

Each character lives under:

- `data/characters/<novel_id>/<character>/PROFILE.md`
- `data/characters/<novel_id>/<character>/NAVIGATION.md`
- `data/characters/<novel_id>/<character>/SOUL.md`
- `data/characters/<novel_id>/<character>/IDENTITY.md`
- `data/characters/<novel_id>/<character>/AGENTS.md`
- `data/characters/<novel_id>/<character>/MEMORY.md`
- `data/characters/<novel_id>/<character>/RELATIONS.md`

Runtime reads `NAVIGATION.generated.md` first, then applies `NAVIGATION.md`, and follows `load_order`.

## Guidance For Agent Integrators

### Recommended Strategy

Prefer this:

```text
take the user's raw request -> send it to zaomeng -> let zaomeng decide act / observe / setup-only
```

Avoid this:

```text
take the raw request -> invent the play pattern outside the engine -> manually simulate the scene -> claim it is act mode
```

### Rules For Skill Layers

- do not manually simulate role chains
- do not treat mode-switch requests as spoken dialogue
- do not treat `zaomeng` as a generic chat model
- do not rely only on legacy JSON assumptions
- do treat markdown persona files as the primary source of truth

## CLI Usage

CLI is still available directly, but it comes after the natural-language guidance because it is the execution layer, not the primary product experience.

### Recommended: automatic intent routing

```bash
python -m src.core.main chat --novel <path-or-name> --mode auto --message "<raw user request>"
```

Examples:

```bash
python -m src.core.main chat --novel data/hongloumeng.txt --mode auto --message "让我扮演贾宝玉和林黛玉聊天"
python -m src.core.main chat --novel data/hongloumeng.txt --session <session_id> --message "妹妹今日可大安了？"
```

```bash
python -m src.core.main chat --novel data/sanguo.txt --mode auto --message "进入刘备、张飞、关羽群聊模式"
python -m src.core.main chat --novel data/sanguo.txt --session <session_id> --message "刘备：二位贤弟，近日战事稍歇。"
```

### Explicit modes

```bash
python -m src.core.main chat --novel <path-or-name> --mode observe --message "<prompt>"
python -m src.core.main chat --novel <path-or-name> --mode act --character <name> --message "<spoken line>"
```

### Other commands

```bash
python -m src.core.main distill --novel <path> [--characters A,B] [--output <dir>] [--force]
python -m src.core.main extract --novel <path> [--output <path>] [--force]
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
