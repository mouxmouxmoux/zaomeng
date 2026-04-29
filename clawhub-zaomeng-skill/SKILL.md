---
name: zaomeng-skill
description: ClawHub 技能包，用于中文小说人物蒸馏、关系抽取与角色对话。
---

# zaomeng 技能（ClawHub）

## 核心定位

- `zaomeng` 是一个以宿主 LLM 为核心的小说人物技能。
- 这个 skill 负责准备小说片段、提示词、参考约束和结构化结果。
- 宿主负责实际生成：蒸馏、关系抽取、单聊、群聊都由宿主 LLM 完成。

## 主要资产

- `prompts/`
- `references/`
- `tools/prepare_novel_excerpt.py`
- `tools/build_prompt_payload.py`

## 标准流程

1. 读取小说内容。
2. 用 `tools/prepare_novel_excerpt.py` 生成 excerpt。
3. 用 `tools/build_prompt_payload.py` 组装 distill 或 relation payload。
4. 将 payload 交给宿主 LLM 生成结果。
5. 蒸馏完成后，再进入 `act` 或 `observe`。

## Chat 调用规则

- 任何 agent 使用这个 skill 时，都应先准备 prompt 输入，再由宿主 LLM 生成结果。
- 群聊与单聊一旦满足执行条件，就直接进入人物对话流程。
- 不要把自然语言启动语直接当成角色台词。
- 不要手工模拟 prompt 输出；按 skill 资产组织宿主调用。

## 自然语言意图映射

- `让我扮演X和Y聊天`
- `我来扮演X，你让Y回我`
- `我说一句，Y回一句`
- `进入 act 模式`

以上按 `act` 启动意图处理。

- `进入刘备、张飞、关羽群聊模式`
- `请让大家围绕这件事各说一句`

以上按 `observe` 启动意图处理。

## 面向用户的表达

用户要求蒸馏人物时：

```text
我先按 zaomeng 的 skill 流程处理这本小说：先准备 excerpt 和 prompt payload，再交给宿主 LLM 做蒸馏。
```

蒸馏完成后，用户要求进入 `act` 或 `observe` 时：

```text
人物档案已经可用，我现在按 zaomeng 的聊天流程进入对应模式。
```

如果是 `act` 启动语：

```text
我先为你建立 act 会话。接下来你说一句角色台词，我再让对方角色按设定回应。
```

如果是 `observe` 启动语：

```text
我先为你建立群聊会话。接下来你可以给场景、话题，或者让某个角色先开口。
```

## Helper 命令

- 准备 excerpt：`py -3 tools/prepare_novel_excerpt.py --novel <路径> [--max-sentences 80] [--max-chars 12000]`
- 组装 prompt payload：`py -3 tools/build_prompt_payload.py --mode distill|relation --novel <路径> [--characters A,B]`

## 产物

- excerpt JSON
- distill prompt payload
- relation prompt payload
- 宿主生成的人物档案
- 宿主生成的人物关系结果
- 人物关系图谱
