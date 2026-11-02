#!/usr/bin/env python3
"""commercial-writing-system v2 校验工具。只用标准库，Python 3.8+。

子命令：
  init   新建或接管项目（只补缺失文件，绝不覆盖）
  gate   开写前门禁：按工作模式检查必备文件，打印必读清单和正典指纹
  check  校验正文、细纲和账本
  merge  把各章状态增量合并进账本（只由账本角色执行）

退出码：0 通过；1 校验未通过；2 配置或用法错误。
"""
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import sys

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UNFILLED_MARK = "CWS:UNFILLED"
CANON_FILES = ["characters", "timeline", "locations", "props", "knowledge", "threads"]
ENTITY_FILES = [("characters", "characters"), ("locations", "locations"), ("props", "props")]
THREAD_ACTIONS = ["planted", "advanced", "echoed", "resolved"]
LEVELS = {"suspects": 1, "knows": 2}

DEFAULT_HOOKS = {
    "required": "every_chapter",
    "min_strength": 2,
    "paywall_min_strength": 4,
    "max_same_run": 1,
    "opening_units": 300,
    "landing_units": 150,
    "max_catch_delay": 3,
}
DEFAULT_THREADS = {"max_gap": 50, "warn_ratio": 0.8}
COMMON_CAPS = set(
    "January February March April May June July August September October November December "
    "Monday Tuesday Wednesday Thursday Friday Saturday Sunday "
    "God Mom Dad Mr Mrs Ms Miss Dr Sir English American French Chinese Christmas Thanksgiving".split()
)


class ConfigError(Exception):
    pass


def read_json(path, default=None):
    if not os.path.exists(path):
        if default is not None:
            return default
        raise ConfigError("找不到文件：%s" % path)
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except ValueError as e:
            raise ConfigError("JSON 解析失败：%s：%s" % (path, e))


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def parse_ranges(spec):
    """'1-5,8' -> [(1, 5), (8, 8)]。"""
    out = []
    for part in str(spec).split(","):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(\d+)(?:-(\d+))?$", part)
        if not m:
            raise ConfigError("无法解析章节范围：%s" % spec)
        a = int(m.group(1))
        out.append((a, int(m.group(2)) if m.group(2) else a))
    return out


def in_ranges(n, ranges):
    return any(a <= n <= b for a, b in ranges)


def term_regex(term, is_regex=False, case_sensitive=False):
    flags = 0 if case_sensitive else re.IGNORECASE
    if is_regex:
        return re.compile(term, flags)
    body = re.escape(term)
    if re.search(r"[A-Za-z0-9]", term):
        body = r"(?<![A-Za-z0-9])" + body + r"(?![A-Za-z0-9])"
    return re.compile(body, flags)


def count_units(text, unit):
    latin = re.findall(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*", text)
    if unit == "words":
        return len(latin)
    return len(re.findall(r"[㐀-鿿]", text)) + len(latin)


def mask_dialogue(text):
    return re.sub(r"“[^”]*”", lambda m: " " * len(m.group(0)), text)


class Chapter:
    HEADING = re.compile(r"^\s*(#+\s|chapter\s+\d+|episode\s+\d+|第\s*[\d一二三四五六七八九十百千零两]+\s*[章集回])", re.I)

    def __init__(self, number, path, text):
        self.number = number
        self.path = path
        lines = text.replace("\r\n", "\n").split("\n")
        start = 0
        for i, line in enumerate(lines):
            if line.strip():
                start = i + 1 if self.HEADING.match(line) else i
                break
        self.start = start
        self.body = "\n".join(lines[start:])
        self.lines = [(start + i + 1, l) for i, l in enumerate(lines[start:]) if l.strip()]

    def line_of(self, pos):
        return self.start + self.body.count("\n", 0, pos) + 1


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, check, msg, chapter=None, line=None):
        self.items.append({"level": level, "check": check, "chapter": chapter, "line": line, "message": msg})

    def err(self, check, msg, chapter=None, line=None):
        self.add("error", check, msg, chapter, line)

    def warn(self, check, msg, chapter=None, line=None):
        self.add("warn", check, msg, chapter, line)

    def count(self, level):
        return sum(1 for i in self.items if i["level"] == level)

    def show(self):
        order = {"error": 0, "warn": 1}
        items = sorted(self.items, key=lambda i: (i["chapter"] or 0, order[i["level"]], i["line"] or 0))
        for i in items:
            where = "第%d章" % i["chapter"] if i["chapter"] else "全书"
            if i["line"]:
                where += " 行%d" % i["line"]
            print("[%s] %-10s %s：%s" % ("错误" if i["level"] == "error" else "告警", i["check"], where, i["message"]))


class Project:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.cfg = read_json(os.path.join(self.root, "project.json"))
        self.mode = self.cfg.get("mode", "new")
        modes = read_json(os.path.join(SKILL_ROOT, "modes", "modes.json"))
        if self.mode not in modes:
            raise ConfigError("未知工作模式：%s（可选：%s）" % (self.mode, "、".join(sorted(modes))))
        self.mode_cfg = modes[self.mode]
        self.style_dir, self.style = self._pack("styles", self.cfg.get("style"), "style.json")
        self.platform_path, self.platform = self._pack("platforms", self.cfg.get("platform"), None)
        self.lang = self.style.get("lang", "en")
        overrides = self.cfg.get("overrides", {})
        self.hooks = dict(DEFAULT_HOOKS)
        self.hooks.update(self.style.get("hooks", {}))
        self.hooks.update(self.platform.get("hooks", {}))
        self.hooks.update(overrides.get("hooks", {}))
        self.length = dict(self.style.get("length", {}))
        self.length.update(self.platform.get("length", {}))
        self.length.update(overrides.get("length", {}))
        self.unit = self.length.get("unit", "words" if self.lang == "en" else "chars")
        self.threads_cfg = dict(DEFAULT_THREADS)
        self.threads_cfg.update(self.style.get("threads", {}))
        self.threads_cfg.update(overrides.get("threads", {}))
        self.multi_agent = bool(self.cfg.get("multi_agent", {}).get("enabled", False))
        self.scope = parse_ranges(self.cfg["scope"]) if self.cfg.get("scope") else None
        self.hook_types = {h["id"]: h for h in read_json(os.path.join(SKILL_ROOT, "references", "hook-types.json"))["types"]}

        self.canon = {}
        for name in CANON_FILES:
            self.canon[name] = read_json(os.path.join(self.root, "canon", name + ".json"), {})
        plan = read_json(os.path.join(self.root, "plan", "chapters.json"), {})
        self.plan = {}
        self.plan_dupes = []
        for row in plan.get("chapters", []):
            if row.get("chapter") in self.plan:
                self.plan_dupes.append(row.get("chapter"))
            self.plan[row.get("chapter")] = row
        self.deltas = {}
        for path in sorted(glob.glob(os.path.join(self.root, "state", "deltas", "*.json"))):
            d = read_json(path)
            if not isinstance(d.get("chapter"), int):
                raise ConfigError("状态增量缺少整数 chapter 字段：%s" % path)
            self.deltas[d["chapter"]] = d
        self.batches = [read_json(p) for p in sorted(glob.glob(os.path.join(self.root, "batches", "*.json")))]
        self.chapters = {}
        self._load_chapters()

    def _pack(self, kind, name, inner):
        if not name:
            raise ConfigError("project.json 缺少 %s 字段" % ("style" if kind == "styles" else "platform"))
        for base in (self.root, SKILL_ROOT):
            if inner:
                d = os.path.join(base, kind, name)
                if os.path.exists(os.path.join(d, inner)):
                    return d, read_json(os.path.join(d, inner))
            else:
                p = os.path.join(base, kind, name + ".json")
                if os.path.exists(p):
                    return p, read_json(p)
        raise ConfigError("找不到配置包：%s/%s" % (kind, name))

    def _load_chapters(self):
        cfg = self.cfg.get("chapters", {})
        pattern = cfg.get("glob", "chapters/ch-*.md")
        rx = re.compile(cfg.get("number_regex", r"(\d+)"))
        for path in sorted(glob.glob(os.path.join(self.root, pattern))):
            m = rx.search(os.path.basename(path))
            if not m:
                continue
            with open(path, encoding="utf-8") as f:
                self.chapters[int(m.group(1))] = Chapter(int(m.group(1)), path, f.read())

    def canon_hash(self):
        h = hashlib.sha256()
        for name in CANON_FILES:
            path = os.path.join(self.root, "canon", name + ".json")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    h.update(name.encode() + b"\0" + f.read() + b"\0")
        return h.hexdigest()[:12]

    def entities(self):
        for fname, key in ENTITY_FILES:
            for e in self.canon[fname].get(key, []):
                yield fname, e

    def character_ids(self):
        return {c.get("id") for c in self.canon["characters"].get("characters", [])}

    def legit_names(self):
        names = set(self.cfg.get("allow_names", []))
        for _, e in self.entities():
            if e.get("name"):
                names.add(e["name"])
            names.update(e.get("aliases", []))
        return names

    def retired_names(self):
        """返回 [(废弃名, 说明)]：实体上的 deprecated_names，加各正典文件顶层的 retired。"""
        out = []
        for _, e in self.entities():
            for d in e.get("deprecated_names", []):
                d = {"name": d} if isinstance(d, str) else d
                note = "现名 %s" % (d.get("replaced_by") or e.get("name"))
                if d.get("note"):
                    note += "；" + d["note"]
                out.append((d["name"], note))
        for fname, _ in ENTITY_FILES:
            for d in self.canon[fname].get("retired", []):
                d = {"name": d} if isinstance(d, str) else d
                out.append((d["name"], d.get("note") or "已从正典删除"))
        return out

    def batch_of(self, chapter):
        for b in self.batches:
            if b.get("status") != "abandoned" and in_ranges(chapter, parse_ranges(b.get("chapters", ""))):
                return b
        return None


# ---------- 正文校验 ----------


def check_names(p, r, ch):
    legit = p.legit_names()
    legit_rx = [term_regex(n, case_sensitive=True) for n in sorted(legit, key=len, reverse=True)]
    spans = [m.span() for rx in legit_rx for m in rx.finditer(ch.body)]

    def covered(a, b):
        return any(x <= a and b <= y and (y - x) > (b - a) for x, y in spans)

    for name, note in p.retired_names():
        hits = [m for m in term_regex(name, case_sensitive=True).finditer(ch.body) if not covered(*m.span())]
        if hits:
            r.err("names", "废弃名“%s”出现 %d 次（%s）" % (name, len(hits), note), ch.number, ch.line_of(hits[0].start()))
    for _, e in p.entities():
        for f in e.get("former_names", []):
            if in_ranges(ch.number, parse_ranges(f.get("chapters", "0"))):
                continue
            hits = [m for m in term_regex(f["name"], case_sensitive=True).finditer(ch.body) if not covered(*m.span())]
            if hits:
                r.err("names", "曾用名“%s”只允许出现在第 %s 章（现名 %s）" % (f["name"], f.get("chapters"), e.get("name")),
                      ch.number, ch.line_of(hits[0].start()))
        if e.get("active_chapters") and not in_ranges(ch.number, parse_ranges(e["active_chapters"])):
            names = [e.get("name")] + list(e.get("aliases", []))
            for n in names:
                m = term_regex(n, case_sensitive=True).search(ch.body)
                if m:
                    r.warn("names", "“%s”的活动范围是第 %s 章，这里又出现了（确认只是被提及）" % (n, e["active_chapters"]),
                           ch.number, ch.line_of(m.start()))
                    break


def check_unknown_names(p, r, selected):
    """英文里句中大写的陌生词，用来发现中途冒出来的新名字。每个词全书只报一次，只告警。"""
    if p.lang != "en":
        return
    known = set(COMMON_CAPS)
    for n in p.legit_names():
        known.update(re.findall(r"[A-Za-z]+", n))
    for n, _ in p.retired_names():
        known.update(re.findall(r"[A-Za-z]+", n))
    reported = set()
    for n in sorted(p.chapters):
        ch = p.chapters[n]
        counts = {}
        for m in re.finditer(r"(?<=[a-z,;:] )[“‘]?([A-Z][a-z]{2,})(?![a-z])", ch.body):
            word = m.group(1)
            if word not in known:
                counts.setdefault(word, []).append(m.start(1))
        for word, hits in sorted(counts.items()):
            if len(hits) >= 2 and word not in reported:
                reported.add(word)
                if selected(n):
                    r.warn("unknown", "“%s”出现 %d 次，正典里没有。新人物走 new_canon_requests；普通专名加进 allow_names"
                           % (word, len(hits)), n, ch.line_of(hits[0]))


def banned_rules(p):
    disabled = set(p.cfg.get("disable_banned", []))
    return [b for b in list(p.style.get("banned", [])) + list(p.cfg.get("extra_banned", [])) if b.get("term") not in disabled]


def check_banned(p, r, selected):
    for rule in banned_rules(p):
        rx = term_regex(rule["term"], rule.get("regex", False), rule.get("case_sensitive", False))
        limit = rule.get("max", 0)
        window = rule.get("window", 1)
        level = rule.get("severity", "error")
        note = "；" + rule["note"] if rule.get("note") else ""
        hits = {}
        for n, ch in p.chapters.items():
            text = mask_dialogue(ch.body) if rule.get("where") == "narration" else ch.body
            hits[n] = list(rx.finditer(text))
        label = rule.get("label") or rule["term"]
        for n in sorted(hits):
            if not selected(n):
                continue
            if window == 1:
                if len(hits[n]) > limit:
                    line = p.chapters[n].line_of(hits[n][limit].start())
                    r.add(level, "banned", "“%s”出现 %d 次，上限 %d%s" % (label, len(hits[n]), limit, note), n, line)
            else:
                total = sum(len(hits.get(k, [])) for k in range(n - window + 1, n + 1))
                if total > limit:
                    r.add(level, "banned", "“%s”在最近 %d 章共 %d 次，上限 %d%s" % (label, window, total, limit, note), n)
                    break


def check_quotes(p, r, ch):
    cfg = p.style.get("quotes", {})
    mode = cfg.get("mode", "none")
    if mode == "script":
        check_script_format(p, r, ch)
        return
    if mode == "none":
        return
    straight_double = [(l, s) for l, s in ch.lines if '"' in s]
    if straight_double:
        r.err("quotes", "直引号 \" 共 %d 行，对白须用弯引号 “ ”" % len(straight_double), ch.number, straight_double[0][0])
    if mode == "en_curly":
        straight = [(l, s) for l, s in ch.lines if re.search(r"[A-Za-z]'[A-Za-z]|'\s", s)]
        if straight:
            r.err("quotes", "直撇号 ' 共 %d 行，须用 ’" % len(straight), ch.number, straight[0][0])
    if mode == "cn_curly":
        corner = [(l, s) for l, s in ch.lines if re.search(r"[「」『』]", s)]
        if corner:
            r.err("quotes", "直角引号共 %d 行，须用 “ ”" % len(corner), ch.number, corner[0][0])
        half = [(l, s) for l, s in ch.lines if re.search(r"[一-鿿][,?!;:][一-鿿]", s)]
        if half:
            r.warn("quotes", "中文之间夹半角标点共 %d 行" % len(half), ch.number, half[0][0])
    # 引号配对。跨段长对白允许上一段不闭合，但下一段必须以开引号起头。
    depth = 0
    for i, (lineno, line) in enumerate(ch.lines):
        for c in line:
            if c == "“":
                if depth:
                    r.err("quotes", "引号未闭合就又开了一个", ch.number, lineno)
                depth = 1
            elif c == "”":
                if not depth:
                    r.err("quotes", "闭引号前面没有开引号（开头引号丢失）", ch.number, lineno)
                depth = 0
        if depth:
            nxt = ch.lines[i + 1][1].lstrip() if i + 1 < len(ch.lines) else ""
            if not nxt.startswith("“"):
                r.err("quotes", "这一段的引号没有闭合（结尾引号丢失）", ch.number, lineno)
            depth = 0
    tag = cfg.get("lost_quote_regex")
    if tag:
        rx = re.compile(tag)
        for lineno, line in ch.lines:
            if "“" not in line and "”" not in line and rx.search(line):
                r.err("quotes", "疑似对白丢了引号：%s" % line.strip()[:50], ch.number, lineno)
    if count_units(ch.body, p.unit) >= cfg.get("min_units_for_dialogue", 300) and "“" not in ch.body:
        r.warn("quotes", "全章没有一个开引号，确认对白引号没有整章丢失", ch.number)


def check_script_format(p, r, ch):
    fmt = p.style.get("format", {})
    scene = re.compile(fmt.get("scene_heading", r"^$"))
    dialogue = re.compile(fmt.get("dialogue_line", r"^$"))
    scenes = sum(1 for _, l in ch.lines if scene.search(l))
    lines = sum(1 for _, l in ch.lines if dialogue.search(l))
    if not scenes:
        r.err("quotes", "剧本没有场次标题（格式：%s）" % fmt.get("scene_hint", ""), ch.number)
    if lines < fmt.get("min_dialogue_lines", 1):
        r.err("quotes", "对白行只有 %d 行，疑似对白格式丢失（格式：%s）" % (lines, fmt.get("dialogue_hint", "")), ch.number)


def check_length(p, r, ch):
    lo, hi = p.length.get("min"), p.length.get("max")
    if not lo and not hi:
        return
    n = count_units(ch.body, p.unit)
    unit = "词" if p.unit == "words" else "字"
    tol = p.length.get("tolerance", 0.15)
    if lo and n < lo:
        hard = n < lo * (1 - tol)
        r.add("error" if hard else "warn", "length", "%d %s，低于下限 %d" % (n, unit, lo), ch.number)
    if hi and n > hi:
        hard = n > hi * (1 + tol)
        r.add("error" if hard else "warn", "length", "%d %s，高于上限 %d" % (n, unit, hi), ch.number)


def check_ending(p, r, ch):
    cfg = p.style.get("ending", {})
    patterns = cfg.get("summary_patterns", [])
    tail = ch.lines[-cfg.get("window_paragraphs", 2):]
    for pat in patterns:
        rx = re.compile(pat, re.IGNORECASE)
        for lineno, line in tail:
            m = rx.search(line)
            if m:
                r.err("ending", "章尾是总结句或升华句（命中“%s”）：%s" % (m.group(0), line.strip()[:60]), ch.number, lineno)


def units_to_chars(p, units):
    return units * 6 if p.unit == "words" else units


def has_keyword(text, keywords):
    low = text.lower()
    return any(k.lower() in low for k in keywords)


# ---------- 细纲与钩子 ----------


def check_hooks(p, r, selected):
    cfg = p.hooks
    rows = [p.plan[k] for k in sorted(k for k in p.plan if isinstance(k, int))]
    for dup in p.plan_dupes:
        r.err("hooks", "细纲里第 %s 章重复" % dup, dup if isinstance(dup, int) else None)
    for n, ch in p.chapters.items():
        if selected(n) and n not in p.plan:
            r.err("hooks", "正文没有对应的细纲条目", n)
    run_type, run_len, prev_n = None, 0, None
    weak = 0
    for row in rows:
        n = row["chapter"]
        hook = row.get("hook") or {}
        need = cfg["required"] == "every_chapter" or (cfg["required"] == "unit_end" and row.get("unit_end"))
        if row.get("final"):
            need = False
        show = selected(n)
        if not hook:
            if need and show:
                r.err("hooks", "细纲没有填钩子（hook.type、hook.strength、hook.text）", n)
            run_type, run_len, prev_n = None, 0, n
            continue
        t, s = hook.get("type"), hook.get("strength")
        if show:
            if t not in p.hook_types:
                r.err("hooks", "钩子类型“%s”不在类型表里（references/hook-types.json）" % t, n)
            if not isinstance(s, int) or not 1 <= s <= 5:
                r.err("hooks", "钩子强度须为 1–5 的整数，现在是 %r" % (s,), n)
            if not hook.get("text"):
                r.err("hooks", "钩子没有写内容（hook.text）", n)
        strength = s if isinstance(s, int) else 0
        if show and strength and strength < cfg["min_strength"] and need:
            r.warn("hooks", "钩子强度 %d 低于平台下限 %d" % (strength, cfg["min_strength"]), n)
        if show and row.get("paywall") and strength < cfg["paywall_min_strength"]:
            r.err("hooks", "付费点章节钩子强度 %d，至少要 %d" % (strength, cfg["paywall_min_strength"]), n)
        weak = weak + 1 if strength and strength <= 2 else 0
        if show and weak == 3:
            r.warn("hooks", "连续 3 章弱钩（强度 ≤2）", n)
        run_len = run_len + 1 if (t == run_type and prev_n == n - 1) else 1
        run_type, prev_n = t, n
        if show and run_len > cfg["max_same_run"]:
            if run_len >= cfg["max_same_run"] + 2:
                r.err("hooks", "钩子类型“%s”已连续 %d 章" % (t, run_len), n)
            else:
                r.warn("hooks", "钩子类型“%s”连续 %d 章，建议换型" % (t, run_len), n)
    check_catches(p, r, selected)


def check_catches(p, r, selected):
    cfg = p.hooks
    for n in sorted(k for k in p.plan if isinstance(k, int)):
        row = p.plan[n]
        prev = p.plan.get(n - 1)
        if not selected(n):
            continue
        ch = p.chapters.get(n)
        hook = row.get("hook") or {}
        if ch and hook.get("keywords"):
            tail = ch.body[-units_to_chars(p, cfg["landing_units"]):]
            if not has_keyword(tail, hook["keywords"]):
                r.warn("hooks", "细纲的钩子没有落在章尾（关键词：%s）" % "、".join(hook["keywords"]), n)
        if not prev or not prev.get("hook"):
            continue
        catch = row.get("catch")
        if not catch or not catch.get("keywords"):
            r.err("catch", "第 %d 章留了钩子，本章细纲要写 catch（mode 和 keywords）说明怎么接" % (n - 1), n)
            continue
        if catch.get("mode") == "delayed":
            by = catch.get("by_chapter")
            if not isinstance(by, int) or by <= n or by > n - 1 + cfg["max_catch_delay"]:
                r.err("catch", "延迟接钩须写 by_chapter，且在第 %d 章之内" % (n - 1 + cfg["max_catch_delay"]), n)
                continue
            if not catch.get("note"):
                r.err("catch", "延迟接钩须写 note，说明为什么不马上接", n)
            target = p.chapters.get(by)
            if target and not has_keyword(target.body, catch["keywords"]):
                r.err("catch", "第 %d 章的钩子约定在第 %d 章接住，那一章没有接（关键词：%s）" % (n - 1, by, "、".join(catch["keywords"])), by)
        elif ch:
            head = ch.body[:units_to_chars(p, cfg["opening_units"])]
            if not has_keyword(head, catch["keywords"]):
                r.err("catch", "开头没有接住上章钩子“%s”（关键词：%s）" % ((prev["hook"].get("text") or "")[:40], "、".join(catch["keywords"])), n)


def check_timeline(p, r, selected):
    last_day, last_n = None, None
    for n in sorted(k for k in p.plan if isinstance(k, int)):
        row = p.plan[n]
        day = row.get("story_day")
        if day is None or row.get("flashback"):
            continue
        if last_day is not None and day < last_day and selected(n):
            r.err("timeline", "story_day %s 早于第 %d 章的 %s。闪回请标 flashback" % (day, last_n, last_day), n)
        last_day, last_n = day, n
    for n, d in p.deltas.items():
        row = p.plan.get(n)
        if selected(n) and row and d.get("story_day") is not None and row.get("story_day") is not None and d["story_day"] != row["story_day"]:
            r.warn("timeline", "状态增量的 story_day %s 和细纲的 %s 不一致" % (d["story_day"], row["story_day"]), n)


# ---------- 伏笔、信息差、增量、批次 ----------


def check_threads(p, r, selected):
    threads = p.canon["threads"].get("threads", [])
    known = {t.get("id"): t for t in threads}
    touches = {k: list(t.get("touches", [])) for k, t in known.items()}
    resolved = {k: t.get("resolved_at") for k, t in known.items()}
    for n in sorted(p.deltas):
        for item in p.deltas[n].get("threads", []):
            tid = item.get("id")
            if tid not in known:
                if selected(n):
                    r.err("threads", "状态增量引用了不存在的伏笔 %s" % tid, n)
                continue
            if item.get("action") not in THREAD_ACTIONS and selected(n):
                r.err("threads", "伏笔 %s 的 action“%s”不合法（%s）" % (tid, item.get("action"), "/".join(THREAD_ACTIONS)), n)
            if resolved.get(tid) and resolved[tid] < n and selected(n):
                r.warn("threads", "伏笔 %s 已在第 %d 章回收，这里又动了它" % (tid, resolved[tid]), n)
            touches[tid].append(n)
            if item.get("action") == "resolved" and not resolved.get(tid):
                resolved[tid] = n
    for n, row in p.plan.items():
        for op in ("plant", "advance", "resolve"):
            for tid in (row.get("threads") or {}).get(op, []):
                if tid not in known and selected(n):
                    r.err("threads", "细纲引用了不存在的伏笔 %s" % tid, n)
                elif n in p.deltas and selected(n) and n not in touches.get(tid, []):
                    r.warn("threads", "细纲要求本章 %s 伏笔 %s，状态增量里没有记录" % (op, tid), n)
    if not p.chapters:
        return
    current = max(p.chapters)
    for t in threads:
        tid = t.get("id")
        planted = t.get("planted")
        if resolved.get(tid) or not isinstance(planted, int) or planted > current:
            continue
        last = max([planted] + [x for x in touches[tid] if x <= current])
        gap = current - last
        limit = t.get("max_gap") or p.threads_cfg["max_gap"]
        name = t.get("name", "")
        if t.get("payoff_by") and current > t["payoff_by"]:
            r.err("threads", "伏笔 %s（%s）约定第 %d 章前回收，已超期" % (tid, name, t["payoff_by"]))
        if gap > limit:
            r.err("threads", "伏笔 %s（%s）最后一次出现在第 %d 章，已隔 %d 章，上限 %d" % (tid, name, last, gap, limit))
        elif gap >= limit * p.threads_cfg["warn_ratio"]:
            r.warn("threads", "伏笔 %s（%s）已隔 %d 章没动，上限 %d" % (tid, name, gap, limit))


def check_knowledge(p, r, selected):
    facts = {f.get("id"): f for f in p.canon["knowledge"].get("facts", [])}
    for fid, f in facts.items():
        for pat in f.get("contradiction_patterns", []):
            rx = re.compile(pat["pattern"], re.IGNORECASE)
            lo, hi = pat.get("from", 1), pat.get("to", 10 ** 9)
            for n, ch in p.chapters.items():
                if selected(n) and lo <= n <= hi:
                    m = rx.search(ch.body)
                    if m:
                        r.err("knowledge", "和事实 %s（%s）矛盾：命中“%s”%s" % (
                            fid, f.get("statement", "")[:30], m.group(0), "；" + pat["note"] if pat.get("note") else ""),
                            n, ch.line_of(m.start()))
    for n in sorted(p.deltas):
        if not selected(n):
            continue
        for item in p.deltas[n].get("knowledge", []):
            fid, who, level = item.get("fact"), item.get("who"), item.get("level", "knows")
            f = facts.get(fid)
            if not f:
                r.err("knowledge", "状态增量引用了不存在的事实 %s" % fid, n)
                continue
            public_at = f.get("public_at")
            if who == "*":
                if public_at != n:
                    r.err("knowledge", "事实 %s 正典约定第 %s 章公开，这里在第 %d 章公开" % (fid, public_at, n), n)
                continue
            if isinstance(public_at, int) and n > public_at:
                r.err("knowledge", "事实 %s 已在第 %d 章公开，%s 不可能第 %d 章才知道（公开情节被清零）" % (fid, public_at, who, n), n)
                continue
            match = [k for k in f.get("knowers", []) if k.get("who") == who and k.get("level", "knows") == level]
            if not match:
                r.err("knowledge", "正典没有登记 %s 在此得知事实 %s（%s）。先改正典，再写章节" % (who, fid, level), n)
            elif match[0].get("chapter") < n:
                r.err("knowledge", "%s 第 %d 章已经知道事实 %s，这里又知道一次（秘密被清零）" % (who, match[0]["chapter"], fid), n)
            elif match[0].get("chapter") > n:
                r.err("knowledge", "%s 按正典第 %d 章才知道事实 %s，这里提前了" % (who, match[0]["chapter"], fid), n)


def build_ledger(p, r, upto=None):
    chars = {}
    props = {}
    for pr in p.canon["props"].get("props", []):
        props[pr.get("id")] = {"holder": pr.get("holder"), "state": pr.get("state"), "history": []}
    threads = {t.get("id"): {"status": t.get("status", "planned"), "last_touch": t.get("planted")}
               for t in p.canon["threads"].get("threads", [])}
    knowledge = {}
    pending = []
    known_chars = p.character_ids()
    merged = []
    for n in sorted(p.deltas):
        if upto is not None and n > upto:
            continue
        d = p.deltas[n]
        merged.append(n)
        for cid, state in (d.get("characters") or {}).items():
            if cid not in known_chars:
                r.err("delta", "状态增量里的人物 id“%s”不在正典里" % cid, n)
                continue
            chars.setdefault(cid, {}).update(state)
            chars[cid]["updated_at"] = n
        for item in d.get("props", []):
            pid = item.get("id")
            if pid not in props:
                r.err("delta", "状态增量引用了不存在的道具 %s" % pid, n)
                continue
            if "from" in item and item["from"] != props[pid]["holder"]:
                r.err("delta", "道具 %s 账上在 %s 手里，增量却写从 %s 转出" % (pid, props[pid]["holder"], item["from"]), n)
            if "holder" in item:
                props[pid]["holder"] = item["holder"]
            if "state" in item:
                props[pid]["state"] = item["state"]
            props[pid]["history"].append({"chapter": n, "holder": props[pid]["holder"], "state": props[pid]["state"]})
        for item in d.get("threads", []):
            if item.get("id") in threads:
                threads[item["id"]] = {"status": item.get("action"), "last_touch": n}
        for item in d.get("knowledge", []):
            knowledge.setdefault(item.get("fact"), {})[item.get("who")] = {"level": item.get("level", "knows"), "chapter": n}
        for req in d.get("new_canon_requests", []):
            pending.append(dict(req, chapter=n))
    return {
        "schema": 2,
        "through_chapter": max(merged) if merged else 0,
        "merged_chapters": merged,
        "canon_hash": p.canon_hash(),
        "characters": chars,
        "props": props,
        "threads": threads,
        "knowledge": knowledge,
        "pending_canon_requests": pending,
    }


def check_deltas(p, r, selected):
    for n in p.chapters:
        if selected(n) and n not in p.deltas:
            (r.err if p.multi_agent else r.warn)("delta", "正文没有状态增量（state/deltas/）", n)
    probe = Report()
    ledger = build_ledger(p, probe)
    for i in probe.items:
        if i["chapter"] is None or selected(i["chapter"]):
            r.items.append(i)
    for req in ledger["pending_canon_requests"]:
        if selected(req["chapter"]):
            r.warn("delta", "有待裁决的新正典请求：%s（%s）" % (req.get("name"), req.get("why", "")), req["chapter"])


def check_batches(p, r, selected):
    if not p.multi_agent:
        return
    seen = {}
    current = p.canon_hash()
    for b in p.batches:
        bid = b.get("id", "?")
        if b.get("status") == "abandoned":
            continue
        ranges = parse_ranges(b.get("chapters", ""))
        if len(ranges) != 1:
            r.err("batch", "批次 %s 必须是一段连续章节，现在是 %s" % (bid, b.get("chapters")))
        if not isinstance(b.get("writer"), str) or not b.get("writer"):
            r.err("batch", "批次 %s 只能有一个写手（writer 须为单个名字）" % bid)
        for role in ("reviewer", "ledger_keeper"):
            if not isinstance(b.get(role), str) or not b.get(role):
                r.err("batch", "批次 %s 缺 %s（须为单个名字）" % (bid, role))
        if b.get("writer") and b.get("writer") == b.get("reviewer"):
            r.err("batch", "批次 %s 的写手和审稿是同一个：%s" % (bid, b["writer"]))
        if b.get("writer") and b.get("writer") == b.get("ledger_keeper"):
            r.err("batch", "批次 %s 的写手不能兼任账本：%s" % (bid, b["writer"]))
        for a, z in ranges:
            for n in range(a, z + 1):
                if n in seen:
                    r.err("batch", "第 %d 章同时属于批次 %s 和 %s" % (n, seen[n], bid), n)
                seen[n] = bid
        if b.get("status") == "merged" and not b.get("review_passed_by"):
            r.err("batch", "批次 %s 已合并但没有审稿通过记录（review_passed_by）" % bid)
        if b.get("review_passed_by") and b.get("review_passed_by") == b.get("writer"):
            r.err("batch", "批次 %s 由写手自己审过" % bid)
    for n in p.chapters:
        if not selected(n):
            continue
        b = p.batch_of(n)
        if not b:
            r.err("batch", "正文不属于任何批次", n)
            continue
        d = p.deltas.get(n)
        if not d:
            continue
        if d.get("batch") != b.get("id"):
            r.err("batch", "状态增量写的批次是 %s，实际是 %s" % (d.get("batch"), b.get("id")), n)
        if d.get("writer") != b.get("writer"):
            r.err("batch", "写手应为 %s，增量里是 %s（同一段连续章节只有一个写手）" % (b.get("writer"), d.get("writer")), n)
        if b.get("status") != "merged" and d.get("canon_hash") != current:
            r.err("batch", "增量的正典指纹 %s 和当前 %s 不一致：写手没加载最新正典。重跑 gate 并重审本章" % (d.get("canon_hash"), current), n)


def check_canon(p, r, selected):
    for fname, key in ENTITY_FILES + [("threads", "threads"), ("knowledge", "facts")]:
        seen = set()
        for e in p.canon[fname].get(key, []):
            eid = e.get("id")
            if not eid:
                r.err("canon", "%s.json 有条目缺 id：%s" % (fname, json.dumps(e, ensure_ascii=False)[:60]))
            elif eid in seen:
                r.err("canon", "%s.json 里 id“%s”重复" % (fname, eid))
            seen.add(eid)
    legit = p.legit_names()
    for name, _ in p.retired_names():
        if name in legit:
            r.err("canon", "“%s”同时是现用名和废弃名，先裁决" % name)
    owners = {}
    for _, e in p.entities():
        for n in [e.get("name")] + list(e.get("aliases", [])):
            if n in owners and owners[n] != e.get("id"):
                r.err("canon", "名字“%s”同时属于 %s 和 %s" % (n, owners[n], e.get("id")))
            owners[n] = e.get("id")
    ids = p.character_ids()
    for f in p.canon["knowledge"].get("facts", []):
        last = {}
        for k in f.get("knowers", []):
            if k.get("who") not in ids:
                r.err("canon", "事实 %s 的知情人“%s”不在 characters.json" % (f.get("id"), k.get("who")))
            if k.get("level", "knows") not in LEVELS:
                r.err("canon", "事实 %s 的 level“%s”不合法" % (f.get("id"), k.get("level")))
            if not isinstance(k.get("chapter"), int):
                r.err("canon", "事实 %s：%s 的 chapter 须为整数" % (f.get("id"), k.get("who")))
                continue
            rank = LEVELS.get(k.get("level", "knows"), 0)
            prev = last.get(k.get("who"))
            if prev and (rank <= prev[0] or k["chapter"] < prev[1]):
                r.err("canon", "事实 %s：%s 的知情进度倒退或重复（只能从猜测到确认，每级一次）" % (f.get("id"), k.get("who")))
            last[k.get("who")] = (rank, k["chapter"])
    for e in p.canon["timeline"].get("events", []):
        if e.get("chapters"):
            parse_ranges(e["chapters"])


CHAPTER_CHECKS = {
    "names": check_names,
    "quotes": check_quotes,
    "length": check_length,
    "ending": check_ending,
}
BOOK_CHECKS = {
    "canon": check_canon,
    "unknown": check_unknown_names,
    "banned": check_banned,
    "hooks": check_hooks,
    "timeline": check_timeline,
    "threads": check_threads,
    "knowledge": check_knowledge,
    "delta": check_deltas,
    "batch": check_batches,
}


def cmd_check(args):
    p = Project(args.project)
    if args.file:
        if not args.chapter:
            raise ConfigError("--file 必须和 --chapter 一起用")
        with open(args.file, encoding="utf-8") as f:
            p.chapters[args.chapter] = Chapter(args.chapter, args.file, f.read())
    if args.chapter:
        ranges = [(args.chapter, args.chapter)]
    elif args.range:
        ranges = parse_ranges(args.range)
    elif args.all:
        ranges = None
    else:
        ranges = p.scope

    def selected(n):
        return ranges is None or in_ranges(n, ranges)

    wanted = set(CHAPTER_CHECKS) | set(BOOK_CHECKS)
    for flag, keep in ((args.only, True), (args.skip, False)):
        if flag:
            names = {x.strip() for x in flag.split(",")}
            unknown = names - set(CHAPTER_CHECKS) - set(BOOK_CHECKS)
            if unknown:
                raise ConfigError("未知检查项：%s" % "、".join(sorted(unknown)))
            wanted = wanted & names if keep else wanted - names

    r = Report()
    for name, fn in BOOK_CHECKS.items():
        if name in wanted:
            fn(p, r, selected)
    for n in sorted(p.chapters):
        if selected(n):
            for name, fn in CHAPTER_CHECKS.items():
                if name in wanted:
                    fn(p, r, p.chapters[n])
    errors, warns = r.count("error"), r.count("warn")
    failed = errors > 0 or (args.strict and warns > 0)
    if args.json:
        print(json.dumps({"ok": not failed, "errors": errors, "warnings": warns, "items": r.items}, ensure_ascii=False, indent=2))
    else:
        r.show()
        print("%s：%d 个错误，%d 个告警（检查了 %d 章）" % ("未通过" if failed else "通过", errors, warns,
                                                sum(1 for n in p.chapters if selected(n))))
    return 1 if failed else 0


# ---------- 门禁 ----------


def is_unfilled(path):
    try:
        with open(path, encoding="utf-8") as f:
            return UNFILLED_MARK in f.read()
    except OSError:
        return False


def cmd_gate(args):
    p = Project(args.project)
    problems = []
    stage_cfg = p.mode_cfg["stages"].get(args.stage)
    if stage_cfg is None:
        raise ConfigError("模式 %s 没有阶段 %s" % (p.mode, args.stage))
    for rel in stage_cfg.get("required_files", []):
        path = os.path.join(p.root, rel)
        if not os.path.exists(path):
            problems.append("缺文件：%s" % rel)
        elif is_unfilled(path):
            problems.append("还没填写（仍有 %s 标记）：%s" % (UNFILLED_MARK, rel))
    for spec in stage_cfg.get("nonempty", []):
        fname, key = spec.split(":")
        if not p.canon[fname].get(key):
            problems.append("正典为空：canon/%s.json 的 %s" % (fname, key))
    if stage_cfg.get("needs_scope") and not p.scope:
        problems.append("project.json 要写 scope（本次要处理的章节范围）")
    if stage_cfg.get("needs_existing_chapters") and not p.chapters:
        problems.append("%s模式要求已有正文，但 chapters 配置没匹配到文件" % p.mode_cfg["label"])
    plan_row = None
    if args.stage == "draft":
        if not args.chapter:
            raise ConfigError("draft 门禁必须带 --chapter")
        n = args.chapter
        plan_row = p.plan.get(n)
        if not plan_row:
            problems.append("第 %d 章没有细纲（plan/chapters.json）" % n)
        else:
            hook = plan_row.get("hook") or {}
            need = p.hooks["required"] == "every_chapter" or (p.hooks["required"] == "unit_end" and plan_row.get("unit_end"))
            if need and not plan_row.get("final") and not (hook.get("type") and hook.get("strength") and hook.get("text")):
                problems.append("第 %d 章细纲的钩子没填全（type、strength、text）" % n)
            prev = p.plan.get(n - 1)
            if prev and prev.get("hook") and not (plan_row.get("catch") or {}).get("keywords"):
                problems.append("第 %d 章细纲没写怎么接上章钩子（catch）" % n)
        first = p.scope[0][0] if p.scope else 1
        if n > first and n - 1 not in p.chapters:
            problems.append("上一章（第 %d 章）还没有正文，不能跳章" % (n - 1))
        if p.multi_agent:
            b = p.batch_of(n)
            if not b:
                problems.append("第 %d 章没有分配批次（batches/）" % n)
            elif args.agent and b.get("writer") != args.agent:
                problems.append("第 %d 章属于批次 %s，写手是 %s，不是 %s" % (n, b.get("id"), b.get("writer"), args.agent))
            elif not args.agent:
                problems.append("多 agent 项目要带 --agent 说明你是谁")
    print("模式：%s｜风格：%s｜平台：%s｜阶段：%s" % (p.mode_cfg["label"], p.cfg.get("style"), p.cfg.get("platform"), args.stage))
    if problems:
        print("门禁未通过：")
        for x in problems:
            print("  - " + x)
        return 1
    print("门禁通过。正典指纹 canon_hash=%s（写进本章状态增量）" % p.canon_hash())
    print("必读清单：")
    for rel in stage_cfg.get("load", []):
        print("  - " + os.path.join(p.root, rel))
    for rel in p.style.get("load", []):
        print("  - " + os.path.join(p.style_dir, rel))
    print("  - " + p.platform_path)
    if plan_row:
        print("本章细纲：" + json.dumps(plan_row, ensure_ascii=False))
        prev = p.plan.get(args.chapter - 1)
        if prev and prev.get("hook"):
            print("上章钩子（开头要接住）：%s" % prev["hook"].get("text"))
        prev_ch = p.chapters.get(args.chapter - 1)
        if prev_ch:
            print("上章全文：" + prev_ch.path)
    return 0


# ---------- 合并账本 ----------


def cmd_merge(args):
    p = Project(args.project)
    r = Report()
    if p.multi_agent:
        for n in p.deltas:
            b = p.batch_of(n)
            if not b:
                r.err("merge", "没有所属批次", n)
            elif b.get("ledger_keeper") != args.agent:
                r.err("merge", "第 %d 章的账本角色是 %s，你是 %s" % (n, b.get("ledger_keeper"), args.agent), n)
            elif not b.get("review_passed_by") or b.get("review_passed_by") == b.get("writer"):
                r.err("merge", "批次 %s 还没有独立审稿通过（review_passed_by）" % b.get("id"), n)
    nums = sorted(p.deltas)
    first = p.scope[0][0] if p.scope else 1
    if nums:
        missing = [n for n in range(first, nums[-1] + 1) if n not in p.deltas]
        if missing:
            r.err("merge", "状态增量不连续，缺第 %s 章" % "、".join(map(str, missing)))
    ledger = build_ledger(p, r)
    check_knowledge(p, r, lambda n: True)
    if r.count("error"):
        r.show()
        print("未合并：%d 个错误。账本没有改动。" % r.count("error"))
        return 1
    write_json(os.path.join(p.root, "state", "ledger.json"), ledger)
    r.show()
    print("已合并到第 %d 章，共 %d 份增量。待裁决的新正典请求 %d 条。" % (
        ledger["through_chapter"], len(ledger["merged_chapters"]), len(ledger["pending_canon_requests"])))
    return 0


# ---------- 初始化 ----------


def cmd_init(args):
    modes = read_json(os.path.join(SKILL_ROOT, "modes", "modes.json"))
    if args.mode not in modes:
        raise ConfigError("未知工作模式：%s" % args.mode)
    root = os.path.abspath(args.path)
    src = os.path.join(SKILL_ROOT, "templates", "project")
    created, kept = [], []
    for base, _, files in os.walk(src):
        for name in files:
            if name == ".gitkeep":
                continue
            s = os.path.join(base, name)
            rel = os.path.relpath(s, src)
            d = os.path.join(root, rel)
            if os.path.exists(d):
                kept.append(rel)
                continue
            os.makedirs(os.path.dirname(d), exist_ok=True)
            with open(s, encoding="utf-8") as f:
                text = f.read().replace("{{SKILL_ROOT}}", SKILL_ROOT)
            with open(d, "w", encoding="utf-8") as f:
                f.write(text)
            created.append(rel)
    for rel in ("chapters", "state/deltas", "batches"):
        os.makedirs(os.path.join(root, rel), exist_ok=True)
    for doc in modes[args.mode].get("scaffold_docs", []):
        s = os.path.join(SKILL_ROOT, "templates", "docs", doc["from"])
        d = os.path.join(root, doc["to"])
        if os.path.exists(d):
            kept.append(doc["to"])
            continue
        os.makedirs(os.path.dirname(d), exist_ok=True)
        with open(s, encoding="utf-8") as f:
            text = f.read()
        with open(d, "w", encoding="utf-8") as f:
            f.write("<!-- %s：填完后删掉这一行 -->\n%s" % (UNFILLED_MARK, text))
        created.append(doc["to"])
    cfg_path = os.path.join(root, "project.json")
    if "project.json" in created:
        cfg = read_json(cfg_path)
        cfg.update({"title": args.title or cfg.get("title", ""), "mode": args.mode, "style": args.style, "platform": args.platform})
        cfg["multi_agent"] = {"enabled": bool(args.multi_agent)}
        write_json(cfg_path, cfg)
    print("新建 %d 个文件，保留已有 %d 个：%s" % (len(created), len(kept), root))
    for rel in kept:
        print("  已存在，未改动：" + rel)
    return 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="commercial-writing-system v2 校验工具")
    sub = ap.add_subparsers(dest="cmd")

    a = sub.add_parser("init", help="新建或接管项目，只补缺失文件")
    a.add_argument("path")
    a.add_argument("--mode", default="new", help="new / continue / rewrite")
    a.add_argument("--style", default="cn-webnovel")
    a.add_argument("--platform", default="cn-serial")
    a.add_argument("--title", default="")
    a.add_argument("--multi-agent", action="store_true")
    a.set_defaults(fn=cmd_init)

    a = sub.add_parser("gate", help="开写前门禁")
    a.add_argument("--project", required=True)
    a.add_argument("--stage", default="draft", help="plan / draft")
    a.add_argument("--chapter", type=int)
    a.add_argument("--agent")
    a.set_defaults(fn=cmd_gate)

    a = sub.add_parser("check", help="校验正文、细纲和账本")
    a.add_argument("--project", required=True)
    a.add_argument("--chapter", type=int)
    a.add_argument("--range", help="如 6-18")
    a.add_argument("--all", action="store_true", help="忽略 project.json 的 scope")
    a.add_argument("--only", help="只跑这些检查，逗号分隔")
    a.add_argument("--skip", help="跳过这些检查，逗号分隔")
    a.add_argument("--file", help="把这个文件当作 --chapter 指定的章节来查（落盘前试查）")
    a.add_argument("--strict", action="store_true", help="告警也算失败")
    a.add_argument("--json", action="store_true")
    a.set_defaults(fn=cmd_check)

    a = sub.add_parser("merge", help="把状态增量合并进账本")
    a.add_argument("--project", required=True)
    a.add_argument("--agent", help="账本角色的名字（多 agent 项目必填）")
    a.set_defaults(fn=cmd_merge)

    args = ap.parse_args(argv)
    if not getattr(args, "fn", None):
        ap.print_help()
        return 2
    try:
        return args.fn(args)
    except ConfigError as e:
        print("配置错误：%s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
