# commercial-writing-system：agent 规则（单一真源）

所有平台共用这一份规则。`SKILL.md`、`CLAUDE.md`、`GEMINI.md` 只负责指向这里。要改规则就改这个文件。

`cws` 指 `python3 <本目录>/scripts/cws.py`。退出码：0 通过，1 未通过，2 配置错误。

## 硬规则

1. **先过门禁再写**。写第 N 章前运行 `cws gate --project . --stage draft --chapter N`（多 agent 项目加 `--agent 你的名字`）。未通过就停下，补齐缺的东西，不要先写一版粗稿。
2. **加载正典再写**。读完门禁打印的必读清单才能动笔，并把门禁给出的 `canon_hash` 写进本章状态增量。
3. **正典优先**。`canon/*.json` 和正文冲突时改正文。确实要改设定，先改正典，再改正文。写手不改正典，只提 `new_canon_requests`。
4. **一章一写**。严格按细纲写。不跳章，不一次生成多章再补校验。
5. **每章都过脚本**。交付前运行 `cws check --project . --chapter N`，退出码不是 0 就修到通过。不能手工声称“已自检”，要贴脚本的结果。
6. **每章输出状态增量**。写入 `state/deltas/ch-NNN.json`，字段见 `references/canon.md`。
7. **章尾强钩与半拍截断**。章尾严格执行半拍截断原则（Mid-Action Cut），绝对禁止动作落地平稳收尾（如脱鞋上床、打开表格），严防阅读饱腹感导致弃读。细纲必须规划 Tier 1 / Tier 2 高转化硬钩，付费卡点严禁使用 `button` 和 `question` 软钩，下一章开头必须接住（`references/hooks.md`）。
8. **规则不串风格**。只遵守项目选定的 `styles/<id>/` 和 `platforms/<id>.json`。中文词表不约束英文稿，影视化手法不是全局规则。
9. **不编造通过**。脚本没跑、跑不了或有未修的错误，都如实告诉用户。规则查不出的问题（语气、节奏、人设）交给审稿，不算脚本通过。
10. **不动原稿**。改写和改编模式下，原稿只读，新稿写到项目的章节目录。

## 工作模式

| 模式 | 什么时候用 | 开工前要有 | 不要求 |
|---|---|---|---|
| `new` 新书 | 从零开始 | 澄清问答、情绪地图、世界规则、关系图、全书大纲、完整正典、细纲 | |
| `continue` 续写 | 接着已有正文写 | 续写说明、从已有正文回填的正典、细纲、`scope` | 情绪地图、世界规则文档、重新走澄清 |
| `rewrite` 改写/改编 | 修改已有稿子或换形式 | 改写说明、正典（含废弃名）、细纲、`scope` | 情绪地图、全书大纲、开书流程 |

门禁按模式判断，机器规则在 `modes/modes.json`。不要要求续写或改写项目补开书文件。详细流程见 `references/modes.md`。

## 流水线

```text
确定模式 → 建正典 → 写细纲（含钩子）→ gate → 写一章 → check → 写状态增量 → 审稿 → 合并账本 → 下一章
                                                                每 10–15 章做一次单元复盘
```

## 多 agent 分工

没有开启多 agent 时，一个 agent 依次担任这些角色。开启后（`project.json` 的 `multi_agent.enabled`）：

| 角色 | 可以改 | 不能改 |
|---|---|---|
| 写手 | 本批次的 `chapters/`、`state/deltas/` | 正典、细纲、账本 |
| 审稿 | `batches/` 的审稿记录 | 正文、正典、账本 |
| 账本 | `state/ledger.json`（只通过 `cws merge`），裁决后的 `canon/` | 正文 |

- 同一段连续章节只有一个写手。
- 审稿和写手不能是同一个 agent。
- 账本只由一个角色合并。
- 每段工作都有批次编号，写在 `batches/`。

完整协议见 `references/multi-agent.md`。

## 文件优先级

`canon/*.json` > `plan/chapters.json` > `state/ledger.json` > `docs/*.md` > 已有正文。

配置优先级：`project.json` 的 `overrides` > 平台 > 风格 > 脚本默认值。

## 命令

| 命令 | 用途 |
|---|---|
| `cws init <目录> --mode M --style S --platform P` | 新建或接管项目，只补缺失文件，不覆盖 |
| `cws gate --project . --stage plan` | 写细纲前的门禁 |
| `cws gate --project . --stage draft --chapter N --agent A` | 写正文前的门禁，打印必读清单和指纹 |
| `cws check --project . --chapter N` | 查一章；不带 `--chapter` 查 `scope` 或全书 |
| `cws check --project . --chapter N --file 草稿路径` | 落盘前试查 |
| `cws check --project . --strict --json` | 告警也算失败；机器可读输出 |
| `cws merge --project . --agent A` | 合并状态增量到账本 |
| `python3 scripts/selftest.py` | 自测校验工具 |

检查项：`canon unknown banned hooks catch timeline threads knowledge delta batch names quotes length ending`。可用 `--only` 和 `--skip` 选择。`catch` 随 `hooks` 运行，不能单独选。

维护本仓库时：改了脚本或配置要跑 `scripts/selftest.py`；`README.md` 和 `README_zh.md` 要同步。
