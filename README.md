# 造梦.skill

[中文](README.md) | [English](README.en.md)

`zaomeng` 是一个本地小说角色工具。

它做三件事：

- 从小说里蒸馏人物
- 从小说里抽取人物关系
- 让这些角色按设定进入群聊或和你对话

它不是普通陪聊机器人。  
它更像一个“小说角色引擎”。

## 先看怎么用

正确顺序不是上来就群聊。  
**第一步永远是先给小说，再蒸馏人物。蒸馏完成后，才能进入群聊或扮演模式。**

用户最常见的使用路径是：

1. 把小说文件附上，或者指定小说文件路径
2. 用自然语言说你要蒸馏谁
3. 蒸馏完成后，再进入群聊或扮演

## 一个完整例子

### 第一步：先附上小说，再说要蒸馏谁

比如你先提供《红楼梦》的小说文本，然后说：

```text
帮我蒸馏林黛玉和贾宝玉
```

系统会先处理小说，生成这两个人物的档案和关系信息。

### 第二步：蒸馏完成后，再进入聊天

这时你再说：

```text
让我扮演贾宝玉和林黛玉聊天
```

系统才会进入“你扮演贾宝玉，林黛玉回应你”的玩法。

接着你可以继续说：

```text
妹妹今日可大安了？
```

系统会把这句当成贾宝玉真正说出口的话，再让林黛玉回话。

### 第三步：如果你想看多人互动，也要在蒸馏之后

比如你先提供《三国演义》，蒸馏刘备、张飞、关羽之后，再说：

```text
进入刘备、张飞、关羽群聊模式
```

然后你再说：

```text
刘备：二位贤弟，近日战事稍歇，倒是难得清闲。
```

系统才会让张飞、关羽接话。

## 你可以直接这样说

### 蒸馏人物

```text
帮我蒸馏林黛玉和贾宝玉
```

```text
请从这本小说里提取刘备、张飞、关羽的人设
```

```text
把《红楼梦》里的宝玉和黛玉蒸馏出来
```

### 蒸馏完成后进入扮演

```text
让我扮演贾宝玉和林黛玉聊天
```

```text
我来扮演刘备，你让关羽和张飞回我
```

### 蒸馏完成后进入群聊

```text
进入刘备、张飞、关羽群聊模式
```

```text
让宝玉、黛玉、宝钗一起聊这一件事
```

### 直接让大家开口

```text
请让大家围绕联合孙权这件事各说一句
```

```text
场景：黛玉初到贾府，请相关人物自然开口
```

## 它能做什么

### 1. 人物蒸馏

从 `.txt` 或 `.epub` 小说中提取主要角色，输出人物档案，包括：

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

### 3. 角色群聊

支持两种聊天方式：

- `observe`
  你给出一个场景、话题或开场白，让角色自然互动
- `act`
  你控制一个角色发言，其余角色按设定回话

### 4. 纠错记忆

如果某句明显不符合人物设定，可以把修正写入记忆。  
后续对话会尽量避开同类偏差。

### 5. Markdown 人格包

当前人物主存储已经是 Markdown，不再以旧版 JSON 为准。

每个角色的文件位于：

- `data/characters/<novel_id>/<角色名>/PROFILE.md`
- `data/characters/<novel_id>/<角色名>/NAVIGATION.md`
- `data/characters/<novel_id>/<角色名>/SOUL.md`
- `data/characters/<novel_id>/<角色名>/IDENTITY.md`
- `data/characters/<novel_id>/<角色名>/AGENTS.md`
- `data/characters/<novel_id>/<角色名>/MEMORY.md`
- `data/characters/<novel_id>/<角色名>/RELATIONS.md`

## 快速开始

### 1. 先准备小说文件

支持：

- `.txt`
- `.epub`

### 2. 先蒸馏，再聊天

以《红楼梦》为例：

```bash
python -m src.core.main distill --novel data/hongloumeng.txt --characters 林黛玉,贾宝玉 --force
python -m src.core.main extract --novel data/hongloumeng.txt --force
```

这一步会生成：

- `data/characters/hongloumeng/<角色名>/`
- `data/relations/hongloumeng/hongloumeng_relations.md`

### 3. 蒸馏完成后，开始聊天

推荐直接用自然语言：

```bash
python -m src.core.main chat --novel data/hongloumeng.txt --mode auto --message "让我扮演贾宝玉和林黛玉聊天"
```

然后继续：

```bash
python -m src.core.main chat --novel data/hongloumeng.txt --session <session_id> --message "妹妹今日可大安了？"
```

如果你想进入多人群聊：

```bash
python -m src.core.main chat --novel data/sanguo.txt --mode auto --message "进入刘备、张飞、关羽群聊模式"
python -m src.core.main chat --novel data/sanguo.txt --session <session_id> --message "刘备：二位贤弟，近日战事稍歇。"
```

## 其他命令

### 查看角色档案

```bash
python -m src.core.main view --character 林黛玉 --novel data/hongloumeng.txt
```

### 保存一次纠错

```bash
python -m src.core.main correct \
  --session <session_id> \
  --message "宝玉打算离家经商" \
  --corrected "宝玉一向厌弃仕途经济，更愿留在诗酒园林之间" \
  --character 贾宝玉
```

## 命令总览

```bash
python -m src.core.main distill --novel <path> [--characters A,B] [--output <dir>] [--force]
python -m src.core.main extract --novel <path> [--output <path>] [--force]
python -m src.core.main chat --novel <path-or-name> --mode auto|observe|act [--character <name>] [--session <id>] [--message <text>]
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
