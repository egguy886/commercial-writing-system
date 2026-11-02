# 风格包

风格规则只在项目选中时生效。v1 的中文词表和影视化规范现在属于 `cn-webnovel`，不再约束其他风格。

| id | 适用 | 不适用 |
|---|---|---|
| `cn-webnovel` | 中文网文：古言、权谋、悬疑、升级流 | 英文稿 |
| `en-romcom` | 英文爱情喜剧、辣味职场恋爱 | 高压黑暗题材 |
| `en-dark-romance` | 英文黑暗浪漫、黑帮恋爱、强取豪夺向 | 轻喜剧 |
| `drama-script` | 竖屏微短剧剧本 | 小说正文 |

## 每个包的结构

```text
styles/<id>/
├── style.json    # 机器规则：语言、引号、禁用表、章尾模式
├── voice.md      # 声音规则，写手必读
├── banned.md     # 禁用表的说明和替换方法，给人和审稿看
└── examples.md   # 正向样例
```

`style.json` 的 `banned` 每条字段：

| 字段 | 含义 |
|---|---|
| `term` | 词或正则 |
| `regex` | `term` 是不是正则，默认否 |
| `label` | 报告里显示的名字，正则时建议填 |
| `max` / `window` | `window` 章内最多出现 `max` 次，默认 1 章 0 次 |
| `where` | 设为 `narration` 时只查叙述，不查对白 |
| `severity` | `error`（默认）或 `warn` |
| `case_sensitive` / `note` | 区分大小写；报告附注 |

## 项目级调整

书专属的禁用词不要改风格包，写进 `project.json`：

```json
{"extra_banned": [{"term": "Bentley", "note": "这本书不写这个车"}], "disable_banned": ["very"]}
```

## 加新风格

复制一个目录改名，放到这里或项目的 `styles/` 下，再把 `project.json` 的 `style` 改成新 id。项目内的同名配置优先。
