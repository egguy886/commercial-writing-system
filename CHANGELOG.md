# 更新记录

## v2.0.0

### 新增
- `AGENTS.md` 作为规则的单一真源，`CLAUDE.md`、`GEMINI.md` 作为薄桥接。
- 无依赖校验工具 `scripts/cws.py`（`init`、`gate`、`check`、`merge`）和自测 `scripts/selftest.py`。
- 机器可读的项目正典：人物（含废弃名和曾用名）、时间线、地点、道具、信息差、伏笔。
- 可插拔配置：`styles/`（cn-webnovel、en-romcom、en-dark-romance、drama-script）和 `platforms/`（cn-serial、en-app-serial、kindle-ku、short-drama）。
- 钩子系统：12 种类型、5 级强度、连续同型检查、付费点强度、下章接钩。
- 工作模式：新书、续写、改写/改编，门禁按模式判断。
- 多 agent 协议：批次、单一写手、审稿分离、状态增量、账本单点合并、正典指纹。
- 示例项目 `examples/mini-romcom/` 和故意写错的 `examples/broken-overlay/`。

### 改动
- `SKILL.md` 缩成按阶段加载的短路由。
- 中文词表和影视化规范移到 `styles/cn-webnovel/`，不再是全局规则。
- 章长不再固定为 1500–3000 字，由平台和项目配置决定。
- 伏笔超期上限改为可配置，默认仍是 50 章。

### 移除
- `templates/04-foreshadowing-props-ledger.md`：由 `canon/threads.json` 和 `canon/props.json` 取代。
- `templates/07-chapter-walkthrough.md`：由 `state/deltas/` 取代。

其余模板移到 `templates/docs/`。
