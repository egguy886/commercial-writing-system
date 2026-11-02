# 商业写作系统（Commercial Writing System）

用 AI 写长篇连载和短剧的流水线。它把最容易写崩的部分交给机器检查：人物改名、引号丢失、秘密被清零、伏笔烂尾、章尾没钩子。

[English](README.md) • [简体中文](README_zh.md)

![License](https://img.shields.io/badge/License-MIT-green.svg) ![Version](https://img.shields.io/badge/Version-v2.0.0-blue.svg) ![Python](https://img.shields.io/badge/Python-3.8%2B%20%E6%97%A0%E4%BE%9D%E8%B5%96-orange.svg)

## 为什么有 v2

v1 的规则全写在文字里，全靠模型自觉遵守。写到几万字后，模型会忘，上下文一滑就开始出错。v1 的风格规则还偏中文古言，用到英语爱情喜剧上就用力过猛。

| 长篇常见的问题 | v2 的做法 |
|---|---|
| 人物中途改名，旧名复活 | 正典记录现用名、废弃名和曾用名，脚本扫描正文 |
| 对白引号丢失，格式混乱 | 脚本检查引号格式、配对和疑似丢引号的对白 |
| 公开过的事又变成秘密 | 正典写明谁在第几章知道什么，增量和正典对不上就报错 |
| 结局和开头矛盾 | 把不能再出现的说法写进正典，脚本拦截 |
| 章尾写总结句，没有钩子 | 细纲必须填钩子类型和强度，脚本查章尾和下章开头 |
| 伏笔埋了就忘 | 伏笔账本自动算间隔，超期报错 |
| 一套文风规则套所有书 | 风格和平台都是可插拔的配置 |
| 换一个 agent 就换一套规矩 | 只有一份 `AGENTS.md`，所有平台都指向它 |

## 快速开始

```bash
git clone https://github.com/egguy886/commercial-writing-system.git ~/.gemini/config/skills/commercial-writing-system
```

先确认工具能跑：

```bash
python3 ~/.gemini/config/skills/commercial-writing-system/scripts/selftest.py
```

为一本书建项目：

```bash
python3 ~/.gemini/config/skills/commercial-writing-system/scripts/cws.py init ~/books/my-book --mode new --style en-romcom --platform en-app-serial
```

然后在 agent 里打开这个目录，说“用商业写作系统开始这本书”。

## 工作模式

| 模式 | 什么时候用 | 开工前要有 |
|---|---|---|
| `new` 新书 | 从零开始 | 澄清问答、情绪地图、世界规则、关系图、大纲、正典、细纲 |
| `continue` 续写 | 接着已有正文写 | 续写说明、回填的正典、细纲 |
| `rewrite` 改写/改编 | 修改稿子或换形式 | 改写说明、正典（含废弃名）、细纲。不用重走开书流程 |

门禁按模式判断。详见 [references/modes.md](references/modes.md)。

## 每一章的流程

```text
细纲（含钩子）→ gate → 读正典 → 写一章 → check → 状态增量 → 审稿 → merge
```

```bash
cws gate  --project . --stage draft --chapter 12   # 没过门禁不开写，并打印必读清单
cws check --project . --chapter 12                 # 退出码 0 才算通过
cws merge --project . --agent ledger-1             # 只由账本角色合并
```

这里的 `cws` 指 `python3 <skill 目录>/scripts/cws.py`。

## 脚本查什么

| 检查项 | 内容 |
|---|---|
| `names` | 废弃名、已删除的名字、超出范围的曾用名、退场后又出现的人物 |
| `unknown` | 正典里没有的陌生专名（英文，只告警） |
| `banned` | 风格禁用词和句式，支持每章或每 N 章的上限 |
| `quotes` | 引号格式和配对、疑似丢引号的对白；剧本查场次和对白格式 |
| `length` | 字数或词数，按平台和项目配置 |
| `ending` | 章尾总结句和升华句 |
| `hooks` / `catch` | 钩子是否填写、类型轮换、付费点强度、章尾是否落地、下章开头是否接住 |
| `threads` | 伏笔超期、引用不存在的伏笔 |
| `knowledge` | 信息差倒退、公开后又清零、提前知道、和事实矛盾的说法 |
| `timeline` | 故事时间倒流 |
| `delta` | 状态增量缺失、道具账对不上、人物 id 错误 |
| `batch` | 批次重叠、写手和审稿是同一个、没加载最新正典 |
| `canon` | 正典自身的冲突：重复 id、同名、现用名和废弃名相撞 |

退出码：0 通过，1 未通过，2 配置错误。`--strict` 让告警也算失败，`--json` 输出机器可读的结果。

脚本能查规则，查不出好不好看。语气、节奏和人设要靠审稿，见 [references/phase-review.md](references/phase-review.md)。

## 风格和平台

| 风格 | 适用 |
|---|---|
| `cn-webnovel` | 中文网文。v1 的词表和影视化手法都归在这里 |
| `en-romcom` | 英文爱情喜剧 |
| `en-dark-romance` | 英文黑暗浪漫 |
| `drama-script` | 微短剧剧本 |

| 平台 | 适用 |
|---|---|
| `cn-serial` | 中文网文连载 |
| `en-app-serial` | 英文连载 App |
| `kindle-ku` | Kindle / KU 长篇 |
| `short-drama` | 竖屏微短剧 |

每个风格包含声音规则、禁用表和正向样例。平台配置章长、付费点、钩子要求和合规项。平台数值是经验默认值，不是官方数据，请以合同和后台为准，差异写进 `project.json` 的 `overrides`。

要加新的风格或平台，见 [styles/README.md](styles/README.md) 和 [platforms/README.md](platforms/README.md)。

## 钩子系统

共 12 种钩子类型，强度分 1–5 级。网文模式默认每章都要钩子。连续同型告警，连续 3 章同型报错。详见 [references/hooks.md](references/hooks.md)。

## 多 agent 协作

- 同一段连续章节只有一个写手。
- 审稿和写手分开。
- 每章输出状态增量。
- 账本只由一个角色合并。
- 批次编号。
- 开写前必须加载正典，增量里要带正典指纹。

这些都由脚本检查。详见 [references/multi-agent.md](references/multi-agent.md)。

## 跨平台

规则只维护在 [AGENTS.md](AGENTS.md)。`SKILL.md` 是按阶段加载的短路由，`CLAUDE.md` 和 `GEMINI.md` 只是指向它的桥接，Codex 直接读取 `AGENTS.md`。

其他平台用符号链接接到同一个目录，不要复制：

```bash
ln -s ~/.gemini/config/skills/commercial-writing-system ~/.claude/skills/commercial-writing-system
```

```bash
ln -s ~/.gemini/config/skills/commercial-writing-system ~/.agents/skills/commercial-writing-system
```

详见 [references/install.md](references/install.md)。

## 目录结构

```text
commercial-writing-system/
├── SKILL.md            # 短路由
├── AGENTS.md           # 规则的单一真源
├── CLAUDE.md、GEMINI.md # 薄桥接
├── scripts/            # cws.py（校验工具）、selftest.py（自测）
├── references/         # 按阶段加载的说明、钩子类型表
├── styles/             # 四种风格
├── platforms/          # 四个平台
├── modes/              # 各模式的门禁规则
├── templates/          # project/ 项目骨架，docs/ 说明文档模板
└── examples/           # 极小的示例项目，以及故意写错的版本
```

## 试一下示例

`examples/mini-romcom/` 是一个 4 章的示例项目，`examples/broken-overlay/` 是故意写错的版本。

```bash
python3 scripts/cws.py check --project examples/mini-romcom --strict
```

```bash
python3 scripts/cws.py check --project examples/mini-romcom --chapter 4 --file examples/broken-overlay/chapters/ch-004.md --only names,banned,quotes,length,ending,hooks
```

前一条通过，后一条会报出废弃名、禁用词、引号错误、字数不足、章尾总结句和没接住钩子。

## 从 v1 升级

- `references/anti-ai-lexicon.md` 和 `cinematographic-constitution.md` 移到了 `styles/cn-webnovel/`，只在选用这个风格时生效。
- 复盘卡和伏笔 Markdown 表被 `state/deltas/`、`canon/threads.json` 取代。
- 已有项目用 `cws init . --mode continue`（或 `rewrite`）接管，不会覆盖已有文件。然后把设定回填进 `canon/`，把 `chapters.glob` 指向已有正文。

完整改动见 [CHANGELOG.md](CHANGELOG.md)。

## 许可证

[MIT](LICENSE)
