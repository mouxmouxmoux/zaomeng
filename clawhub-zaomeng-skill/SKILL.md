---
name: zaomeng-skill
description: ClawHub 技能包，用于 zaomeng 的中文小说人物蒸馏、关系抽取与角色对话。
---

# zaomeng 技能（ClawHub）

## 先看这个

- `zaomeng` 现在是 **LLM-first** 工作流，不再把规则模板回复当成正常主路径。
- 使用 skill 时先做 **LLM preflight**：先确认当前宿主或运行环境能提供可生成的 LLM，再进入蒸馏、关系抽取、单聊或群聊。
- 宿主里如果已经有可用模型，优先直接复用宿主能力；不要要求用户重复配置一套新的模型。
- 如果宿主是 OpenClaw、Hermes 或其他 agent 容器，优先使用宿主已注入的能力，而不是手搓一套额外桥接。
- `runtime/config.yaml` 仍然可以作为 CLI 直跑时的显式配置来源，但不是在宿主内运行 skill 时的第一来源。
- 不要因为运行时没单独填写 `runtime/config.yaml` 就停下来让用户二选一。
- 不要提示“去配置 runtime/config.yaml 才能继续群聊”。
- 不要在 OpenClaw 中因为看到 `llm.provider=local-rule-engine` 就要求用户去改 `runtime/config.yaml`。
- 如果宿主已经配置了 OpenAI、Anthropic 或 Ollama，或者已经注入了宿主 LLM，就直接继续执行用户请求。
- 只有在宿主和环境里都拿不到可生成 LLM 时，才中止工作流，并明确告诉用户先补齐模型配置；这时不要继续蒸馏，更不要退回“规则模式”。

## 引擎准备

- 这个 skill 包已经内嵌最小可运行 runtime，优先直接使用 skill 包内运行时，不要再去克隆外部仓库。
- 运行时入口：
  - `runtime/zaomeng_cli.py`
  - runtime 自持 wrapper 位于 `runtime/src/core/main.py`、`runtime/src/core/runtime_factory.py`、`runtime/src/core/logging_utils.py`
  - 共享实现位于 `runtime/src/core/cli_app.py`、`runtime/src/core/runtime_parts.py`、`runtime/src/core/logging_setup.py`
- 默认数据目录位于 `runtime/data/...`
- 依赖要求：
  - 必需：`PyYAML`
  - 可选：`tiktoken`
  - 可选：`ebooklib`，仅在读取 `.epub` 时需要
- 命令建议：
  - Windows / PowerShell 优先使用 `py -3 runtime/zaomeng_cli.py ...`
  - 其他环境可使用 `python runtime/zaomeng_cli.py ...`

## 正常执行顺序

- 开始执行前，先确认当前环境确实能调用 LLM。
- 用户给了小说文件并要求蒸馏时，先走真实工作流：`distill`；必要时再执行 `extract`。
- 蒸馏完成后，再进入 `chat` / `observe` / `act`。
- 除非用户明确要求手工模拟模板输出，否则不要退化成“读 prompt/schema 后手工拼一版结果”。

## Chat 调用规则

- 优先直接调用 `runtime/zaomeng_cli.py`，不要绕过它手工拼内部模块。
- 默认规则：任何 agent 使用这个 skill 调 `chat` 时，都应带 `--message`。
- 群聊 / 单聊请求一旦满足 `chat --message` 的执行条件，就直接执行，不要插入“配置 LLM / 继续规则模式”这种额外选择题。
- Windows / PowerShell 首选用法：
  - `py -3 runtime/zaomeng_cli.py chat --novel <路径或名称> --mode auto --message "<用户原话>"`
  - `py -3 runtime/zaomeng_cli.py chat --novel <路径或名称> --mode observe --message "<提示语>"`
  - `py -3 runtime/zaomeng_cli.py chat --novel <路径或名称> --mode act --character <角色名> --message "<用户台词>"`
  - `py -3 runtime/zaomeng_cli.py chat --novel <路径或名称> --mode auto|observe|act [--character <角色名>] --session <id> --message "<提示语或台词>"`

## 自然语言意图映射

- `让我扮演X和Y聊天`、`我来扮演X，你让Y回我`、`我说一句，Y回一句`、`进入 act 模式`：按 `act` 启动意图处理。
- 这类启动语不能直接当成角色台词喂给引擎；先让 CLI 建立或恢复 `act` 会话。
- 后续用户真正进入对白时，再继续用 `--session <id> --message "<用户台词>"`。
- `进入刘备、张飞、关羽群聊模式`：按 `observe` 启动意图处理。
- `请让大家围绕这件事各说一句`：按真实 `observe` 单轮执行。

## 面对用户的标准回复

总原则：面向用户时，只说“现在要做什么”和“接下来会发生什么”，不要把调试日志、依赖排查过程、源码路径判断过程直接讲给用户听。

### 1. 用户要求蒸馏人物

推荐说法：

```text
我先按 zaomeng 的真实流程处理这本小说，前提是当前环境能直接调用到 LLM。确认可用后，我就开始蒸馏你指定的人物档案。
```

### 2. 蒸馏完成后，用户要求进入 act / observe

推荐说法：

```text
人物档案已经可用，我现在按 zaomeng 的聊天流程进入对应模式。
```

如果是 act 启动语：

```text
我先为你建立 act 会话。接下来你说一句角色台词，我再让对方角色按设定回应。
```

如果是 observe 启动语：

```text
我先为你建立群聊会话。接下来你可以给场景、话题，或者让某个角色先开口。
```

不要说：

```text
我这里还没检测到可生成 LLM。请先确认宿主已经提供模型能力，或在 CLI 运行环境里补齐 OpenAI / Anthropic / Ollama 配置；可用后我再继续蒸馏或聊天。
```

### 3. 当前环境拿不到 LLM

只允许简短说明：

```text
我现在没有检测到可用的 LLM，所以先不进入 zaomeng 工作流。请直接补齐宿主模型能力，或在 CLI 运行环境里配置 OpenAI / Anthropic / Ollama 后再继续。
```

不要说：

```text
那我先用模板规则顶着跑。
```

## 其他命令

- 蒸馏：`py -3 runtime/zaomeng_cli.py distill --novel <路径> [--characters A,B] [--force]`
- 关系抽取：`py -3 runtime/zaomeng_cli.py extract --novel <路径> [--output <路径>] [--force]`
- 查看角色：`py -3 runtime/zaomeng_cli.py view --character <角色名> [--novel <路径或名称>]`
- 保存纠错：`py -3 runtime/zaomeng_cli.py correct --session <id> --message <原句> --corrected <修正句> [--character <角色名>]`

## 人格文件与记忆说明

- 当前主存储为 Markdown 人格包，不再以 JSON 为准。
- 人格文件默认位于 `runtime/data/characters/<novel_id>/<角色名>/`
- 运行时会先读 `NAVIGATION.generated.md`，再叠加 `NAVIGATION.md`，然后按 `load_order` 加载人格文件。
- 用户长期修正和 `/correct` 的结果会写入对应角色的 `MEMORY.md`
