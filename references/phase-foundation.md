# 新书：澄清和地基

只有 `new` 模式需要走这一步。续写和改写见 `references/modes.md`。

## 澄清问答

写设定前先问 3–5 个问题，能从用户的话里判断的就不问：

1. **核心驱动力**：主角最底层的欲望是什么？（复仇、夺权、生存、解密、守护、被爱……）
2. **节奏**：紧凑高压，还是张弛有度？
3. **红线**：哪些内容绝对不能碰？
4. **结局**：大团圆、留白，还是惨烈余韵？
5. **形式**：语言、风格、发布平台、预计长度？

设定里用三种标记：`[核心红线]` 不可妥协，`[需要澄清]` 待定，`[可选特性]` 锦上添花。

## 地基文件

| 文件 | 内容 | 模板 |
|---|---|---|
| `docs/00-emotion-map.md` | 一句话卖点，红线，全书情绪极值点 | `templates/docs/00-emotion-map.md` |
| `docs/02-world-rules.md` | 舞台、阶层和反挑刺规则 | `templates/docs/02-worldbuilding-rules.md` |
| `docs/03-relationships.md` | Mermaid 关系图 | `templates/docs/03-relationship-matrix-mermaid.md` |
| `docs/05-master-outline.md` | 分卷、真相层级和结局 | `templates/docs/05-master-outline.md` |
| `canon/*.json` | 人物、时间线、地点、道具、信息差、伏笔 | `references/canon.md` |

模板里的示例多取自古言权谋，换题材时要替换，不要照搬。需要写人物小传时用 `templates/docs/01-character-profile.md`，放在 `docs/`，但事实以 `canon/characters.json` 为准。

## 开头和结局要对得上

写大纲时就把结局依赖的事实写进 `knowledge.json` 的 `contradiction_patterns` 或 `threads.json` 的 `payoff_by`。比如开头说他从不下厨，结局却写他做了十年饭，就要在正典里明确哪个是真的、什么时候揭开。

每一项填完，删掉文件开头的 `CWS:UNFILLED` 标记，再运行：

```bash
cws gate --project . --stage plan
```
