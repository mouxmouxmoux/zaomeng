# 造梦.skill

[中文](README.md) | [English](README.en.md)

本项目是一个把小说文本转成“可运行角色资产”的本地工具链，用来做：

- 人物蒸馏
- 关系抽取
- 受约束角色对话
- 用户纠错写入记忆
- OpenClaw / Hermes / ClawHub 等 Agent 集成

它不是通用陪聊模型。它的目标是让角色“像这个人”，而不是“像一个会说话的 AI”。

## 先看这个：现在推荐用自然语言驱动

如果你正在通过 OpenClaw、Hermes、ClawHub 或其他 Agent 工具接入 `zaomeng`，**优先把用户原话直接交给 `chat --mode auto`**，而不是先在外层手写模式判断，再拼接成剧情演示。

推荐心智模型：

- 用户说“进入某种玩法”时，这是**意图启动语**
- 用户真正开始扮演角色说话时，这才是**角色台词**
- `zaomeng` 应该负责把前者识别成模式切换，把后者送进角色引擎

### 自然语言到模式的映射

下面这些话，应该优先理解成 **进入 `act` 模式**：

- `让我扮演贾宝玉和林黛玉聊天`
- `我来扮演贾宝玉，你让林黛玉回我`
- `我说一句，黛玉回一句`
- `进入宝黛 act 模式`
- `我要扮演刘备`

这类句子是“开模式”，**不是宝玉/刘备已经说出口的话**。  
正确行为应该是：

1. 建立或恢复 `act` 会话
2. 记住用户控制的是谁
3. 等用户下一句真正开口，再驱动对方角色回话

下面这些话，应该优先理解成 **进入 `observe` 模式**：

- `进入刘备、张飞、关羽群聊模式`
- `开启宝黛群聊`
- `切到 observe 模式`

下面这些话，则是 **直接执行一轮 `observe`**，而不是仅仅切模式：

- `请让大家围绕这件事各说一句`
- `场景：黛玉初到贾府，请相关人物自然开口`
- `让众人围绕联合孙权这件事分别表态`

### 给 Agent 的一句话规则

如果用户像是在“描述玩法”，就先切模式。  
如果用户像是在“以角色身份开口”，再把这句当成真正台词送进去。

### OpenClaw / Hermes 这类工具该怎么理解

推荐外层工具这样处理：

- 收到用户原话，优先原样传给 `zaomeng`
- 默认走 `chat --mode auto`
- 不要在外层手动模拟“宝玉会怎么说、黛玉会怎么回”
- 不要把“让我扮演宝玉和黛玉聊天”改写成“好，我来模拟一段宝黛互动”

也就是说，**自然语言描述玩法是第一入口，CLI 只是执行层**。

## 典型自然语言玩法

### 1. 用户想进入一对一行动模式

用户说：

```text
让我扮演贾宝玉和林黛玉聊天
```

预期行为：

- 系统进入 `act`
- 用户控制 `贾宝玉`
- 系统优先让 `林黛玉` 作为主要回应对象
- 返回一个可继续的 `session`

接着用户再说：

```text
妹妹今日可大安了？
```

这时才应把这句当成贾宝玉真正的台词，驱动林黛玉回应。

### 2. 用户想进入多人观察模式

用户说：

```text
进入刘备、张飞、关羽群聊模式
```

预期行为：

- 系统进入 `observe`
- 会话角色范围缩到这三人
- 等待用户给出场景或首句

接着用户说：

```text
刘备：二位贤弟，近日战事稍歇，倒是难得清闲。
```

这时再让张飞、关羽基于各自设定回应。

### 3. 用户想让大家直接开口

用户说：

```text
请让大家围绕联合孙权这件事各说一句
```

预期行为：

- 这是一次真实的 `observe` 发言
- 不要只回复“已进入 observe 模式”
- 应直接输出相关角色的回应

## 核心能力

### 1. 人物蒸馏

从 `.txt` 或 `.epub` 小说中提取主要角色，输出人格化角色档案，包括：

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

### 2. 关系抽取

从小说中生成关系图谱，当前核心字段包括：

- `trust`
- `affection`
- `power_gap`
- `conflict_point`
- `typical_interaction`

### 3. 角色对话

支持两种模式：

- `observe`
  你给出场景或引导语，角色们围绕它自然互动
- `act`
  你控制一个角色发言，其余角色按设定和关系状态回话

对话过程支持：

- `/save`
- `/reflect`
- `/correct 角色|对象|原句|修正句|原因`
- `/quit`

### 4. 纠错记忆

如果某句明显 OOC，可以把修正写入本地记忆。后续生成时会尽量规避相同偏差。

### 5. Markdown 人格包

当前人物主存储已经是 Markdown，不再以旧版 JSON 为准。

每个角色会落在：

- `data/characters/<novel_id>/<角色名>/PROFILE.md`
- `data/characters/<novel_id>/<角色名>/NAVIGATION.md`
- `data/characters/<novel_id>/<角色名>/SOUL.md`
- `data/characters/<novel_id>/<角色名>/IDENTITY.md`
- `data/characters/<novel_id>/<角色名>/AGENTS.md`
- `data/characters/<novel_id>/<角色名>/MEMORY.md`
- `data/characters/<novel_id>/<角色名>/RELATIONS.md`

运行时会先读取 `NAVIGATION.generated.md`，再叠加 `NAVIGATION.md`，按 `load_order` 加载人格层。

## 给 Agent 集成方的建议

### 推荐调用策略

优先这样做：

```text
拿到用户原话 -> 直接交给 zaomeng -> 让 zaomeng 判断 act / observe / setup-only
```

不推荐这样做：

```text
拿到用户原话 -> 外层代理自己脑补玩法 -> 手动模拟剧情 -> 再说“这是 act 模式”
```

### Skill 层应该遵守的原则

- 不要手动模拟角色接龙
- 不要把“进入某模式”误写成角色对白
- 不要把 `zaomeng` 当成普通聊天模型
- 不要只依赖旧版 JSON 字段理解角色
- 要把 Markdown 人格文件当成当前主设定来源

## CLI 用法

CLI 仍然可直接调用，但这里放在后面。  
如果你是人类开发者或在调试集成，可以直接用。

### 推荐：自动意图解析

```bash
python -m src.core.main chat --novel <path-or-name> --mode auto --message "<用户原话>"
```

例如：

```bash
python -m src.core.main chat --novel data/hongloumeng.txt --mode auto --message "让我扮演贾宝玉和林黛玉聊天"
python -m src.core.main chat --novel data/hongloumeng.txt --session <session_id> --message "妹妹今日可大安了？"
```

```bash
python -m src.core.main chat --novel data/sanguo.txt --mode auto --message "进入刘备、张飞、关羽群聊模式"
python -m src.core.main chat --novel data/sanguo.txt --session <session_id> --message "刘备：二位贤弟，近日战事稍歇。"
```

### 显式指定模式

```bash
python -m src.core.main chat --novel <path-or-name> --mode observe --message "<提示语>"
python -m src.core.main chat --novel <path-or-name> --mode act --character <name> --message "<角色台词>"
```

### 其他命令

```bash
python -m src.core.main distill --novel <path> [--characters A,B] [--output <dir>] [--force]
python -m src.core.main extract --novel <path> [--output <path>] [--force]
python -m src.core.main view --character <name> [--novel <path-or-name>]
python -m src.core.main correct --session <id> --message <raw> --corrected <fixed> [--character <name>] [--target <name>] [--reason <text>]
```

## 项目结构

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
