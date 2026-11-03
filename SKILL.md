---
name: commercial-writing-system
description: |
  长篇连载和短剧的写作流水线（Commercial Writing System v2.1）：开新书、续写、改写或改编；章尾强钩硬化与半拍截断原则（防软化/防饱腹感/高转化硬钩体系）；用机器可读的正典和校验脚本防止人物改名、引号丢失、秘密清零、伏笔烂尾；可切换风格（中文网文、英文爱情喜剧、英文黑暗浪漫、短剧剧本）和平台；支持多 agent 分工。
  触发词：商业写作系统、写小说、开新书、续写、改写小说、改编、网文写作、长篇连载、章尾钩子、章尾防软化、半拍截断、强悬念、付费卡点、人物一致性、去AI味写小说、出海小说、write a novel, continue my novel, rewrite chapters, web serial, romance novel, cliffhanger, mid-action cut, keep characters consistent.
---

# 商业写作系统 v2.1：路由

硬规则的唯一来源是同目录的 `AGENTS.md`。先读它，再按下表只加载当前阶段需要的文件。不要一次读完所有文件。

下文的 `cws` 指 `python3 <本目录>/scripts/cws.py`。

## 第一步：确定工作模式

| 用户的情况 | 模式 |
|---|---|
| 从零开始一本书 | `new` 新书 |
| 已有正文，要接着写 | `continue` 续写 |
| 已有稿子要修改，或换形式 | `rewrite` 改写/改编 |

项目已有 `project.json` 时以其中的 `mode` 为准。没有时运行 `cws init <目录> --mode <模式> --style <风格> --platform <平台>`。只有判断不出模式、风格或平台时才问用户。

## 第二步：按阶段加载

| 阶段 | 先运行 | 加载 |
|---|---|---|
| 确定模式和接手 | | `references/modes.md` |
| 建正典 | | `references/canon.md` |
| 新书的澄清和地基 | | `references/phase-foundation.md`，`templates/docs/` |
| 写细纲 | `cws gate --project . --stage plan` | `references/phase-planning.md`，`references/hooks.md` |
| 写正文 | `cws gate --project . --stage draft --chapter N` | 门禁打印的必读清单，`references/phase-drafting.md` |
| 审稿 | `cws check --project . --chapter N` | `references/phase-review.md` |
| 单元复盘、伏笔管理 | `cws check --project .` | `references/foreshadowing-tracker-spec.md` |
| 多 agent 协作 | | `references/multi-agent.md` |
| 选题材节拍 | | `references/genre-playbooks.md` |
| 安装到其他平台 | | `references/install.md` |

风格和平台的规则分别在 `styles/<id>/` 和 `platforms/<id>.json`，由门禁列入必读清单。不要把某个风格的规则用到别的风格上。
