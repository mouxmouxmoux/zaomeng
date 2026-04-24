---
name: hermes-zaomeng
description: Hermes Agent adapter for zaomeng local novel distillation, relation extraction, and roleplay chat.
---

# Hermes Adapter

## Supported Tasks

1. Distill character profiles from `.txt` and `.epub` novels.
2. Build pairwise relationship graphs for same-sentence co-occurring characters.
3. Run immersive `observe` or `act` chat sessions.
4. Persist and retrieve correction memories to reduce repeated OOC behavior.

## Invocation Mapping

- Distillation: `python -m src.core.main distill --novel ...`
- Relationship extraction: `python -m src.core.main extract --novel ...`
- Session chat: `python -m src.core.main chat --novel ... --mode ...`
- Character view: `python -m src.core.main view --character ... [--novel ...]`
- Manual correction: `python -m src.core.main correct --session ... --message ... --corrected ...`

## Behavioral Constraints

- Use chunk strategy with token window and overlap for long novels.
- Save durable artifacts under novel-scoped `data/` directories.
- Show local token/cost stats from `llm_client.py`.
- Enforce the daily budget from `config.yaml`.
- Do not rely on external cloud model providers.
