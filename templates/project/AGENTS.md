# 本项目的 agent 规则

本项目用 commercial-writing-system v2 写作。真源在：`{{SKILL_ROOT}}`

开工前按顺序做：

1. 读 `{{SKILL_ROOT}}/AGENTS.md`，按其中的硬规则工作。
2. 读本目录的 `project.json`，确认工作模式、风格和平台。
3. 写正文前运行门禁，并读完它打印的必读清单：

```bash
python3 "{{SKILL_ROOT}}/scripts/cws.py" gate --project . --stage draft --chapter N
```

`canon/*.json` 是本书的正典。正文和正典冲突时改正文。
