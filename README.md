# Commercial Writing System

A production pipeline for writing long serial fiction and short dramas with AI agents. It hands the failures that wreck long books to machine checks: characters changing names, lost dialogue quotes, secrets that reset, dropped foreshadowing, and chapters that end without a hook.

[English](README.md) • [简体中文](README_zh.md)

![License](https://img.shields.io/badge/License-MIT-green.svg) ![Version](https://img.shields.io/badge/Version-v2.0.0-blue.svg) ![Python](https://img.shields.io/badge/Python-3.8%2B%20no%20dependencies-orange.svg)

## Why v2

In v1, every rule lived in prose and relied on the model to follow it. After a few tens of thousands of words, models forget and errors creep in as context slides away. The v1 style rules also leaned toward Chinese historical fiction, which is far too heavy for an English rom-com.

| Common long-form failure | What v2 does |
|---|---|
| A character changes name mid-book, or an old name returns | The canon records current, deprecated, and former names, and a script scans the text |
| Dialogue quotes go missing or formats drift | A script checks quote format, pairing, and dialogue that looks unquoted |
| A public event becomes a secret again | The canon says who learns what in which chapter, and mismatched deltas fail |
| The ending contradicts the opening | Statements that must not recur go in the canon, and a script blocks them |
| Chapters end on a summary with no hook | Outlines must give a hook type and strength; a script checks the chapter ending and the next opening |
| Foreshadowing is planted and forgotten | The thread ledger computes gaps and fails overdue threads |
| One style rulebook for every book | Styles and platforms are pluggable configuration |
| Every agent follows different rules | There is one `AGENTS.md`, and every platform points to it |

## Quick start

```bash
git clone https://github.com/egguy886/commercial-writing-system.git ~/.gemini/config/skills/commercial-writing-system
```

Confirm the tool runs:

```bash
python3 ~/.gemini/config/skills/commercial-writing-system/scripts/selftest.py
```

Create a project for a book:

```bash
python3 ~/.gemini/config/skills/commercial-writing-system/scripts/cws.py init ~/books/my-book --mode new --style en-romcom --platform en-app-serial
```

Then open that folder in your agent and ask it to start the book with the Commercial Writing System.

## Working modes

| Mode | When | Needed before drafting |
|---|---|---|
| `new` | Starting from nothing | Clarifying questions, emotion map, world rules, relationship map, outline, canon, chapter plan |
| `continue` | Extending existing chapters | Continuation brief, canon backfilled from the text, chapter plan |
| `rewrite` | Revising a draft or adapting it to another form | Rewrite brief, canon including deprecated names, chapter plan. No new-book process |

Gates are evaluated per mode. See [references/modes.md](references/modes.md).

## The per-chapter loop

```text
chapter plan with hook → gate → load canon → write one chapter → check → state delta → review → merge
```

```bash
cws gate  --project . --stage draft --chapter 12   # no drafting until this passes; prints the required reading
cws check --project . --chapter 12                 # exit code 0 means pass
cws merge --project . --agent ledger-1             # only the ledger role merges
```

Here `cws` means `python3 <skill folder>/scripts/cws.py`.

## What the script checks

| Check | Covers |
|---|---|
| `names` | Deprecated and retired names, former names outside their range, characters back after their exit |
| `unknown` | Proper nouns missing from the canon (English only, warning only) |
| `banned` | Style-banned words and patterns, with per-chapter or per-N-chapter limits |
| `quotes` | Quote format and pairing, dialogue that looks unquoted; scene and dialogue format for scripts |
| `length` | Word or character count, from platform and project settings |
| `ending` | Summary or moralizing sentences at the chapter end |
| `hooks` / `catch` | Hook present, type rotation, paywall strength, hook lands at the end, next opening picks it up |
| `threads` | Overdue foreshadowing, references to missing threads |
| `knowledge` | Knowledge moving backward, resets after a public event, learning too early, contradicting statements |
| `timeline` | Story time running backward |
| `delta` | Missing state deltas, prop ledger mismatches, wrong character ids |
| `batch` | Overlapping batches, writer also acting as reviewer, canon not loaded at its latest version |
| `canon` | Conflicts inside the canon: duplicate ids, shared names, a name both current and deprecated |

Exit codes: 0 pass, 1 fail, 2 configuration error. `--strict` makes warnings fail, and `--json` gives machine-readable output.

The script checks rules. It can't tell whether a chapter is any good. Voice, pacing, and character need a reviewer: see [references/phase-review.md](references/phase-review.md).

## Styles and platforms

| Style | For |
|---|---|
| `cn-webnovel` | Chinese web novels. The v1 lexicon and cinematic techniques now live here |
| `en-romcom` | English romantic comedy |
| `en-dark-romance` | English dark romance |
| `drama-script` | Vertical short-drama scripts |

| Platform | For |
|---|---|
| `cn-serial` | Chinese web serials |
| `en-app-serial` | English coin-unlock serial apps |
| `kindle-ku` | Kindle and Kindle Unlimited novels |
| `short-drama` | Vertical short dramas |

Each style has voice rules, a banned list, and positive examples. Each platform sets chapter length, paywall guidance, hook requirements, and compliance items. Platform numbers are rule-of-thumb defaults, not official data. Your contract and platform dashboard take priority: put the differences in `overrides` in `project.json`.

To add a style or platform, see [styles/README.md](styles/README.md) and [platforms/README.md](platforms/README.md).

## Hook system (Hardened Cliffhangers & Mid-Action Cut)

There are 12 hook types, grouped into three tiers:
- **Tier 1 Hard Conversion Hooks** (`danger`, `caught`, `reveal`, `desire`, `reversal`): Main drivers for serialized retention and required on paywalls.
- **Tier 2 Propulsion Hooks** (`message`, `deadline`, `showdown`, `decision`): Standard rotation for narrative momentum.
- **Tier 3 Soft Hooks** (`question`, `button`): High drop-off risk; restricted in pay-per-chapter serials and **strictly forbidden on paywalls**.

Core principles:
- **Starvation over Satiety**: Never give the reader emotional closure at the chapter end. Banter, reflection, and quiet character moments belong *mid-chapter*; chapter ends must cut off on high tension.
- **Mid-Action Cut Principle**: Never cut after an action resolves (e.g. going to bed, opening a file). Cut mid-action, mid-interruption, or as a crisis lands.
- **Platform strength thresholds**: Serial app baseline hook strength is 3 (warning on consecutive weak hooks ≤2); short drama baseline is 4; paywall chapters require strength 4–5. See [references/hooks.md](references/hooks.md).

## Multi-agent work

- One writer per contiguous chapter range.
- Reviewers are separate from writers.
- Every chapter produces a state delta.
- Only one role merges the ledger.
- Work is organized into numbered batches.
- Writers must load the canon first, and each delta carries a canon fingerprint.

The script enforces all of these. See [references/multi-agent.md](references/multi-agent.md).

## Cross-platform use

Rules are maintained only in [AGENTS.md](AGENTS.md). `SKILL.md` is a short router that loads files by stage, `CLAUDE.md` and `GEMINI.md` are thin bridges to it, and Codex reads `AGENTS.md` directly.

Connect other platforms to the same folder with symlinks instead of copies:

```bash
ln -s ~/.gemini/config/skills/commercial-writing-system ~/.claude/skills/commercial-writing-system
```

```bash
ln -s ~/.gemini/config/skills/commercial-writing-system ~/.agents/skills/commercial-writing-system
```

See [references/install.md](references/install.md).

## Repository layout

```text
commercial-writing-system/
├── SKILL.md            # short router
├── AGENTS.md           # single source of truth for rules
├── CLAUDE.md, GEMINI.md # thin bridges
├── scripts/            # cws.py (checker), selftest.py (self-test)
├── references/         # stage-by-stage guides, hook type table
├── styles/             # four styles
├── platforms/          # four platforms
├── modes/              # gate rules for each mode
├── templates/          # project/ scaffold, docs/ document templates
└── examples/           # a tiny example project and a deliberately broken version
```

## Try the example

`examples/mini-romcom/` is a four-chapter example project, and `examples/broken-overlay/` is a deliberately broken version.

```bash
python3 scripts/cws.py check --project examples/mini-romcom --strict
```

```bash
python3 scripts/cws.py check --project examples/mini-romcom --chapter 4 --file examples/broken-overlay/chapters/ch-004.md --only names,banned,quotes,length,ending,hooks
```

The first command passes. The second reports deprecated names, banned words, quote errors, a short chapter, a summary ending, and a hook that wasn't picked up.

## Upgrading from v1

- `references/anti-ai-lexicon.md` and `cinematographic-constitution.md` moved to `styles/cn-webnovel/` and apply only when that style is selected.
- Walkthrough cards and the Markdown foreshadowing table are replaced by `state/deltas/` and `canon/threads.json`.
- Adopt an existing project with `cws init . --mode continue` (or `rewrite`), which never overwrites existing files. Then backfill your settings into `canon/` and point `chapters.glob` at your existing chapters.

See [CHANGELOG.md](CHANGELOG.md) for all changes.

## License

[MIT](LICENSE)
