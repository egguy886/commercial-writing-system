# 写细纲

长篇以 10–15 章为一个单元推进，不要一口气规划到结局再无序长跑。

每个单元开始前：

1. 用 `templates/docs/06-unit-plan-10ch.md` 写单元预案，放在 `docs/units/`。
2. 把逐章细纲写进 `plan/chapters.json`（字段见 `references/canon.md`）。
3. 每章都要有钩子和接钩（`references/hooks.md`）。
4. 涉及信息差和伏笔的变化，先确认正典里有。没有就先改正典。
5. 运行校验：

```bash
cws check --project . --only canon,hooks,timeline,threads
```

6. 请用户确认方向，再开始写正文。用户已明确说不用确认时除外。

## 细纲要防的问题

- **公开情节被清零**：第 40 章全公司都知道了，第 55 章又成了秘密。写细纲时查 `knowledge.json`。
- **钩子同型**：连续几章都是收到短信。查类型分布。
- **章尾偏软 / 饱腹感结尾**：细纲规划钩子时，禁止将章节停在“日常解决”、“安然入睡”、“平稳交接”上。连载 App 与短剧优先选用 Tier 1 高转化硬钩（`danger`, `caught`, `reveal`, `desire`, `reversal`）。付费卡点（`paywall: true`）严禁使用 `button` 或 `question`！
- **没有代价**：主角这一单元有没有失去什么？
- **配角消失**：重要配角隔太久没出现，要安排，或者在正典里写明退场。

风格和题材的节拍见 `styles/<id>/voice.md` 和 `references/genre-playbooks.md`。
