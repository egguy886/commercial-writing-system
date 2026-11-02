# 多 agent 协议

在 `project.json` 设 `"multi_agent": {"enabled": true}` 后，脚本会强制执行下面的规则。agent 可以来自不同平台，因为它们都只靠项目里的文件协作。

## 角色

| 角色 | 负责 | 可以改 | 不能改 |
|---|---|---|---|
| 统筹（可以是人） | 写细纲，开批次，裁决争议 | `plan/`、`batches/` | 正文 |
| 写手 | 写一段连续章节 | 本批次的 `chapters/`、`state/deltas/` | 正典、细纲、账本 |
| 审稿 | 审稿，给出通过或打回 | 批次文件的审稿字段 | 正文、正典、账本 |
| 账本 | 合并增量，裁决新正典请求，更新正典 | `state/ledger.json`、`canon/` | 正文 |

## 硬规则

1. **同一段连续章节只有一个写手**。批次的 `writer` 是单个名字，`chapters` 是一段连续范围。
2. **审稿和写手分开**。`reviewer` 不能等于 `writer`，账本也不能由写手兼任。
3. **每章输出状态增量**。没有增量的章节不算完成。
4. **账本只由一个角色合并**。只有批次的 `ledger_keeper` 能运行 `cws merge`。不要手改 `state/ledger.json`。
5. **批次编号**。一切工作都归属到 `batches/` 里的一个批次。
6. **开写前必须加载正典**。写手先跑 `gate`，读完必读清单，把 `canon_hash` 写进增量。

## 批次文件：batches/B003.json

```json
{
  "id": "B003",
  "chapters": "21-30",
  "writer": "gemini-flash-1",
  "reviewer": "claude-opus-1",
  "ledger_keeper": "codex-1",
  "canon_hash": "4ceaf6a3fed1",
  "status": "open",
  "review_passed_by": null
}
```

`status`：`open`（在写）、`review`（在审）、`merged`（已合并）、`abandoned`（作废，章节可以重新分配）。

## 一个批次的流程

```text
统筹：写细纲，开批次
  ↓
写手：gate --chapter N --agent 我 → 读必读清单 → 写一章 → check --chapter N → 写增量 → 下一章
  ↓ 全部写完，status 改为 review
审稿：check --range 21-30 --strict → 读正文（references/phase-review.md）
  ├─ 打回：写清章号和问题，写手修改，重跑 check
  └─ 通过：填 review_passed_by
  ↓
账本：merge --agent 我 → 裁决 pending_canon_requests → status 改为 merged
  ↓
统筹：开下一批。下一批的写手从账本读取最新状态
```

## 正典改动

- 只有账本能改 `canon/`。
- 正典一改，指纹就变。还在进行中的批次，脚本会报“写手没加载最新正典”。受影响的写手要重跑 `gate`，重新确认已写章节，并更新增量里的 `canon_hash`。
- 已合并的批次不受影响。

## 脚本能证明什么

`canon_hash` 只证明写手跑过当前版本的门禁，证明不了它真的读了。写手是否遵守正典，要靠 `check` 和审稿来发现。

## 单 agent 项目

不开启时，同一个 agent 依次担任所有角色，不查批次。状态增量缺失只告警。但写完一段后，最好换一个新会话或新模型来审。
