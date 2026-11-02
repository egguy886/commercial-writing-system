# 项目正典：字段说明

正典是一本书的事实来源，全部是 JSON，脚本能直接校验。说明性的文字放 `docs/`，事实放这里。

```text
my-book/
├── project.json          # 模式、风格、平台、章节路径
├── canon/                # 正典：写手只读
│   ├── characters.json
│   ├── timeline.json
│   ├── locations.json
│   ├── props.json
│   ├── knowledge.json    # 谁在第几章知道什么
│   └── threads.json      # 伏笔
├── plan/chapters.json    # 逐章细纲
├── docs/                 # 说明文档，按模式不同
├── chapters/             # 正文
├── state/deltas/         # 每章的状态增量（写手写）
├── state/ledger.json     # 账本（只由 cws merge 生成）
└── batches/              # 批次
```

完整示例见 `examples/mini-romcom/`。

## project.json

| 字段 | 含义 |
|---|---|
| `mode` | `new`、`continue`、`rewrite` |
| `style`、`platform` | 对应 `styles/`、`platforms/` 的 id |
| `chapters.glob` | 正文路径，相对项目目录，也可以是绝对路径。默认 `chapters/ch-*.md` |
| `chapters.number_regex` | 从文件名提取章号，默认取第一串数字 |
| `scope` | 本次处理的章节，如 `"6-50"`。续写和改写必填。默认只查这个范围，`--all` 查全部 |
| `multi_agent.enabled` | 是否开启批次和角色校验 |
| `allow_names` | 正典外允许出现的专名（地名、品牌等） |
| `extra_banned`、`disable_banned` | 书专属的禁用词；关掉风格里的某些词 |
| `overrides` | 覆盖 `length`、`hooks`、`threads` |

## characters.json

```json
{
  "characters": [{
    "id": "ruth",
    "name": "Ruth Calder",
    "aliases": ["Ruth", "Dr. Calder"],
    "former_names": [{"name": "Ruthie Bell", "chapters": "12,40", "note": "只在这两章的旧信件里出现"}],
    "deprecated_names": [{"name": "Rachel Calder", "replaced_by": "Ruth Calder", "note": "旧稿的名字"}],
    "active_chapters": "1-120",
    "age": 58,
    "voice": "平静，话少"
  }],
  "retired": [{"name": "Marcus", "note": "已删除"}]
}
```

三种旧名字的区别：

| 字段 | 含义 | 脚本行为 |
|---|---|---|
| `deprecated_names` | 废弃名：旧稿用过，这本书的世界里从未存在 | 出现即报错 |
| `former_names` | 曾用名：故事里真实存在的旧名字 | 超出 `chapters` 范围报错 |
| `retired` | 被删除或合并的人物、地点、道具 | 出现即报错 |

`active_chapters` 是可选的活动范围，超出时告警，用来防止已退场的人物又跑回来。除 `id`、`name` 外，其他字段可以按书的需要加（外貌、弱点、称呼规则等）。`locations.json` 和 `props.json` 用同样的 `aliases`、`deprecated_names`、`retired`、`active_chapters`。

脚本按大小写精确匹配名字，并且不会把现用名里的子串误报成废弃名（`李四海` 不算 `李四`）。

## timeline.json

```json
{
  "calendar_note": "第一年 3 月 2 日是周一",
  "events": [{"id": "E1", "chapters": "1-48", "story_day": 1, "date": "Y1-03-02", "summary": "…"}]
}
```

细纲和增量里的 `story_day` 必须单调不减，闪回要标 `"flashback": true`。

## props.json

```json
{"props": [{"id": "P01", "name": "the silver compass", "aliases": ["compass"], "holder": "owen", "state": "真品"}]}
```

`holder` 是开局时的持有人。之后的变化写在状态增量里，账本负责核对。

## knowledge.json：谁在第几章知道什么

```json
{
  "facts": [{
    "id": "F1",
    "statement": "匿名信是 Owen 写的",
    "knowers": [
      {"who": "priya", "level": "suspects", "chapter": 7, "how": "认出信纸"},
      {"who": "priya", "level": "knows", "chapter": 27, "how": "看到草稿"}
    ],
    "public_at": 60,
    "contradiction_patterns": [
      {"pattern": "(?:nobody|no one) knows", "from": 61, "note": "第 60 章已公开"}
    ]
  }]
}
```

规则：

- 每人每级只有一次。`level` 只能从 `suspects` 到 `knows`，不能倒退。
- 增量里写“X 在第 N 章得知 F”，必须和正典完全对上。早于正典算提前，晚于正典算清零。
- `public_at` 之后，任何人都不能再“第一次得知”。
- `contradiction_patterns` 是正文里不能再出现的说法，用 `from`、`to` 限定章节。可以用来锁定结局和开头的事实，防止前后矛盾。

## threads.json：伏笔

```json
{
  "threads": [{
    "id": "T01",
    "name": "银罗盘",
    "kind": "prop",
    "planted": 1,
    "payoff_by": 40,
    "max_gap": 10,
    "touches": [1, 2]
  }]
}
```

`max_gap` 不写时用项目默认值（50 章，`overrides.threads.max_gap` 可调）。超过上限或过了 `payoff_by` 还没回收就报错。接近上限时告警。状态靠增量推进，不用手改。生命周期见 `references/foreshadowing-tracker-spec.md`。

## plan/chapters.json：细纲

```json
{
  "chapters": [{
    "chapter": 12,
    "title": "The Second Letter",
    "pov": "dana",
    "story_day": 5,
    "batch": "B002",
    "emotion": "紧张",
    "summary": "…",
    "threads": {"plant": [], "advance": ["T03"], "resolve": []},
    "catch": {"mode": "direct", "keywords": ["footsteps", "Priya"], "note": "门外的人开口"},
    "hook": {"type": "button", "strength": 2, "text": "Second letter? Then who wrote the first?", "keywords": ["first"]},
    "paywall": false
  }]
}
```

钩子字段见 `references/hooks.md`。最后一章标 `"final": true`，不要求钩子。

## 状态增量：state/deltas/ch-NNN.json

每章一份，写手写。

```json
{
  "chapter": 12,
  "batch": "B002",
  "writer": "writer-a",
  "canon_hash": "4ceaf6a3fed1",
  "story_day": 5,
  "pov": ["dana"],
  "summary": "一两句话",
  "characters": {"dana": {"location": "办公室", "condition": "左脚踝扭伤", "mood": "嘴硬"}},
  "props": [{"id": "P01", "from": "owen", "holder": "dana", "state": "其实是仿品"}],
  "threads": [{"id": "T03", "action": "advanced", "note": "…"}],
  "knowledge": [{"fact": "F2", "who": "priya", "level": "suspects"}],
  "new_canon_requests": [{"type": "character", "name": "Marta", "why": "门卫，后面还会出现"}]
}
```

- `threads[].action`：`planted`、`advanced`、`echoed`、`resolved`。
- `knowledge[].who` 写 `"*"` 表示公开事件，章号必须等于 `public_at`。
- 需要的新人物、新地点写进 `new_canon_requests`，不要自己改正典。

## 从已有书稿回填

1. 从设定文档里列出现用名、别名和要删除的名字。
2. 把“谁知道什么”的表写成 `knowledge.json`，章号照抄。
3. 把伏笔账本写成 `threads.json`，已回收的标 `resolved_at`。
4. 运行 `cws check --project . --all --only canon,names,unknown`，把报出来的陌生专名归入正典或 `allow_names`。
