---
name: hermes-dreamforge
description: 造梦.skill 的 Hermes Agent 适配协议。用于基于小说文本进行分块蒸馏、关系网抽取、角色群聊和 OOC 纠错，使用本地规则引擎输出可追踪 JSON 档案并控制预算。
---

# Hermes Adapter

## Supported Tasks

1. Distill character minds from `.txt` / `.epub` novels.
2. Build pairwise relationship graph in canonical key format `<A>_<B>`.
3. Run immersive roleplay chat with `observe` / `act` modes.
4. Persist and retrieve correction memories to reduce repeated OOC behavior.

## Invocation Mapping

- Distillation: `distill --novel ...`
- Relationship extraction: `extract --novel ...`
- Session chat: `chat --novel ... --mode ...`
- Character profile read: `view --character ...`
- Manual correction: `correct --session ... --message ... --corrected ...`

## Behavioral Constraints

- Use chunk strategy with token window + overlap for long context.
- Save every durable artifact under `data/` JSON directories.
- Show token/cost stats from `llm_client.py` on each local generation turn.
- Enforce daily budget limit from `config.yaml` key `cost_control.daily_budget_usd`.
- Do not rely on external cloud model providers.
