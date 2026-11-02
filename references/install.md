# 安装和跨平台接入

规则只有一份，放在仓库的 `AGENTS.md`。各平台要做的只是找到这个目录。

## 本机的真源位置

```text
~/.gemini/config/skills/commercial-writing-system    # 真实目录，也是 git 仓库
~/.gemini/antigravity/skills -> ~/.gemini/config/skills   # 整个 skills 目录是符号链接
```

所以 Gemini 和 Antigravity 已经能找到它，不需要再做任何事。其他平台链接到真实目录，不要复制，否则会出现两份规则。

## 各平台接法

下面的命令供你自己执行，安装脚本不会替你改这些位置。先把真源路径存进变量：

```bash
SRC="$HOME/.gemini/config/skills/commercial-writing-system"
```

### Claude Code

用户级 skill 放在 `~/.claude/skills/`：

```bash
ln -s "$SRC" "$HOME/.claude/skills/commercial-writing-system"
```

入口是 `SKILL.md`。在项目里工作时，`CLAUDE.md` 通过 `@AGENTS.md` 导入规则。

### Codex

Codex 自动读取工作目录的 `AGENTS.md`，也支持 `SKILL.md` 格式的 skill。用户级目录按 Codex 当前文档使用 `~/.agents/skills/`：

```bash
ln -s "$SRC" "$HOME/.agents/skills/commercial-writing-system"
```

如果你的 Codex 版本没有发现这个 skill，请查 [Codex 的 skill 文档](https://developers.openai.com/codex/skills)，确认当前版本的目录。

### Gemini CLI 和 Antigravity

全局目录是 `~/.gemini/config/skills/`，本仓库已经在那里。Antigravity 也读取 `~/.gemini/antigravity/skills/`，本机这个路径已经链接过去。不同版本的目录见 [Antigravity 的 skill 文档](https://www.antigravity.google/docs/skills)。

`GEMINI.md` 里写了 `@./AGENTS.md`。部分模型可能不展开导入，所以文件里还加了一句“先读取 `AGENTS.md`”作为兜底。

### 其他支持 Agent Skills 或 AGENTS.md 的工具

把目录链接到该工具的 skills 目录。如果只支持规则文件，就把规则文件指向 `AGENTS.md`，内容不要复制。

## 接入具体的书

skill 是工具，每本书还要有自己的项目目录：

```bash
python3 "$SRC/scripts/cws.py" init ~/books/my-book --mode new --style en-romcom --platform en-app-serial
```

`init` 会在项目里生成 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md`，指向本机的 skill 路径。这样换哪个 agent 打开这本书，都会读到同一份规则和正典。`init` 不覆盖已有文件，接管已有项目也安全。

## 依赖

只需要 Python 3.8 或更高版本，不用装任何包。
