# 更新记录

## v2.1.0

### 新增与核心优化
- **章尾强钩硬化与防软化机制**：
  - 确立商业网文付费转化核心哲学：坚决给读者“生理饥饿感（Visceral Urgency）”，严防“文学饱腹感（Aesthetic Satiety）”导致次日弃读。
  - 引入**“半拍截断原则（Mid-Action Cut）”**：严禁在动作完成或平稳落地后收笔（如脱鞋入睡、打开表格），强制在动作执行一半被意外打断、新危机迫降或秘密撕裂的瞬间硬性截断。
  - 钩子类型分级：划分为 **Tier 1 高转化硬钩**（`danger`, `caught`, `reveal`, `desire`, `reversal`）、**Tier 2 推进型中钩**（`message`, `deadline`, `showdown`, `decision`）与 **Tier 3 软钩**（`question`, `button`）。
- **平台配置分级与付费卡点防软化**：
  - `en-app-serial`（英文连载App）与 `cn-serial`（中文网文连载）最低钩子强度底线提升至 `3`，连续弱钩（强度 ≤2）直接告警。
  - `short-drama`（竖屏短剧）钩子强度底线拉高至 `4`，付费点强制 `5`，平台禁用 `button`。
  - 付费卡点章节（`paywall: true`）强制禁用 `button`（金句收束）与 `question`（细节微疑），必须使用 Tier 1 硬钩。
- **校验工具 `cws.py` 增强**：
  - 新增 `paywall_forbidden_types` 校验：付费点使用软钩直接报错。
  - 新增平台 `disallowed_types` 校验：命中平台禁用类型直接报错。
  - 增强连续弱钩追踪告警。
  - 自测套件扩充至 62 项全量通过测试。

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
