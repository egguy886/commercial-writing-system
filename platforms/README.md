# 平台配置

每个 JSON 管四件事：章长（`length`）、钩子要求（`hooks`）、付费点（`paywall`）、合规项（`compliance`）。

| id | 适用 |
|---|---|
| `cn-serial` | 中文网文连载 |
| `en-app-serial` | 英文连载 App |
| `kindle-ku` | Kindle / KU 长篇 |
| `short-drama` | 竖屏微短剧 |

数值是经验默认值，不是平台官方数据，每个文件的 `provenance` 都写明了这一点。合同或编辑的要求优先，写进项目的 `project.json`：

```json
{"overrides": {"length": {"min": 1500, "max": 2200}, "hooks": {"paywall_min_strength": 5}}}
```

优先级：`project.json` 的 `overrides` > 平台 > 风格 > 脚本默认值。

**加新平台**：复制一个 JSON 改名，放到这里或项目的 `platforms/` 下，再把 `project.json` 的 `platform` 改成新 id。项目内的同名配置优先。

`hooks.required` 可选 `every_chapter`（默认）、`unit_end`（只查细纲标了 `unit_end` 的章）、`none`。
