# 示例

- `mini-romcom/`：极小的 4 章多 agent 项目，应当全部通过。
- `broken-overlay/`：盖在上面的故意写错的文件。第 4 章和相关细纲、增量都有问题，应当被查出来。

```bash
python3 scripts/selftest.py
```

只看正常项目：

```bash
python3 scripts/cws.py check --project examples/mini-romcom --strict
```

把写错的章节当作第 4 章试查（只查正文，不落盘）：

```bash
python3 scripts/cws.py check --project examples/mini-romcom --chapter 4 --file examples/broken-overlay/chapters/ch-004.md --only names,banned,quotes,length,ending,hooks
```
