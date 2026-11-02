# 工作模式

模式写在 `project.json` 的 `mode`，门禁按模式判断，机器规则在 `modes/modes.json`。

## new：新书

1. `cws init <目录> --mode new --style <风格> --platform <平台>`
2. 按 `references/phase-foundation.md` 做澄清，填 `docs/`。填完一份就删掉它第一行的 `CWS:UNFILLED` 标记。
3. 建正典（`references/canon.md`）。
4. `cws gate --project . --stage plan`，通过后写细纲。
5. 逐章写。

## continue：续写

接着已有正文往下写，不重走开书流程。

1. 在书稿目录运行 `cws init . --mode continue --style <风格> --platform <平台>`。已有文件不会被覆盖。
2. 改 `project.json`：`chapters.glob` 指向已有正文，`scope` 写本次要写的范围。
3. 读已有正文，回填正典，重点是现用名、谁知道什么、未回收的伏笔。
4. 填 `docs/continuation-brief.md`，贴 2–3 段最能代表这本书语气的原文。
5. 运行 `cws check --project . --all --only canon,names,unknown`，确认正典和已有正文对得上。
6. 写接下来这一段的细纲。第一章的 `catch` 要接住已有正文的结尾。
7. 逐章写。

`scope` 之外的旧章节默认不查，只作为伏笔和信息差的依据。

## rewrite：改写和改编

修改已有稿子，或者把小说改成短剧等其他形式。不要求情绪地图和全书大纲。

1. 建一个新目录作为项目，`cws init <新目录> --mode rewrite --style <风格> --platform <平台>`。
2. 原稿只读。在 `docs/rewrite-brief.md` 写清位置、问题、保留什么、必须改什么和章节对照。
3. 建正典。旧稿的错误名字写进 `deprecated_names` 或 `retired`，这是改写模式防止旧名复活的关键。
4. `project.json` 写 `scope`。要先诊断旧稿，可以把 `chapters.glob` 暂时指向原稿，运行 `cws check --project . --all`，确认问题规模。诊断完再指回新章节目录。
5. 写改动范围的细纲，再逐章写。

改编时，`style` 和 `platform` 选目标形式的（例如 `drama-script`、`short-drama`）。把长篇压缩成固定集数，可以先用环境里的 `write-screenplay`，再回到这里校验。

## 中途换模式

改 `project.json` 的 `mode`，再运行一次 `cws init . --mode <新模式>` 补上缺的说明文档，然后重跑门禁。正典和正文都不用动。
