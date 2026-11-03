#!/usr/bin/env python3
"""自测：示例项目要通过，故意写错的版本要被查出来，四种风格和三种模式都要能跑。"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cws  # noqa: E402

ROOT = cws.SKILL_ROOT
EXAMPLE = os.path.join(ROOT, "examples", "mini-romcom")
OVERLAY = os.path.join(ROOT, "examples", "broken-overlay")
failures = []


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = cws.main(list(argv))
    return code, out.getvalue()


def expect(name, ok, detail=""):
    print("%s %s" % ("通过" if ok else "失败", name))
    if not ok:
        failures.append(name)
        if detail:
            print(detail)


def copy_tree_over(src, dst):
    for base, _, files in os.walk(src):
        for f in files:
            s = os.path.join(base, f)
            d = os.path.join(dst, os.path.relpath(s, src))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy(s, d)


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def test_clean(tmp):
    code, out = run("check", "--project", EXAMPLE, "--strict")
    expect("干净示例严格模式退出码 0", code == 0, out)
    project = os.path.join(tmp, "clean")
    shutil.copytree(EXAMPLE, project)
    code, out = run("gate", "--project", project, "--stage", "draft", "--chapter", "4", "--agent", "writer-a")
    expect("写手门禁通过并给出正典指纹", code == 0 and "canon_hash=" in out and "必读清单" in out, out)
    code, out = run("gate", "--project", project, "--stage", "draft", "--chapter", "4", "--agent", "writer-z")
    expect("别的写手被门禁拦下", code == 1 and "写手是 writer-a" in out, out)
    code, out = run("gate", "--project", project, "--stage", "draft", "--chapter", "9", "--agent", "writer-a")
    expect("没有细纲的章节被门禁拦下", code == 1 and "没有细纲" in out, out)
    code, out = run("merge", "--project", project, "--agent", "writer-a")
    expect("写手不能合并账本", code == 1 and "账本角色" in out, out)
    expect("拒绝合并后账本没有落盘", not os.path.exists(os.path.join(project, "state", "ledger.json")))
    code, out = run("merge", "--project", project, "--agent", "keeper-c")
    expect("账本角色能合并", code == 0, out)
    with open(os.path.join(project, "state", "ledger.json"), encoding="utf-8") as f:
        ledger = json.load(f)
    expect("账本记录道具易手", ledger["props"]["key"]["holder"] == "theo")
    expect("账本记录伏笔回收", ledger["threads"]["T1"]["status"] == "resolved")


def test_broken(tmp):
    project = os.path.join(tmp, "broken")
    shutil.copytree(EXAMPLE, project)
    copy_tree_over(OVERLAY, project)
    code, out = run("check", "--project", project, "--json")
    report = json.loads(out)
    expect("写错的版本退出码 1", code == 1)
    msgs = [(i["check"], i["message"]) for i in report["items"]]
    wanted = {
        "废弃人名 Greg": ("names", "Greg"),
        "废弃地点 Apex Tower": ("names", "Apex Tower"),
        "禁用词 predatory": ("banned", "predatory"),
        "假转折句式": ("banned", "It wasn"),
        "直引号": ("quotes", "直引号"),
        "直撇号": ("quotes", "直撇号"),
        "对白丢引号": ("quotes", "丢了引号"),
        "引号未闭合": ("quotes", "没有闭合"),
        "字数不足": ("length", "低于下限"),
        "章尾总结句": ("ending", "总结句"),
        "连续同型钩子": ("hooks", "连续 3 章"),
        "付费点强度不足": ("hooks", "付费点"),
        "缺钩子": ("hooks", "没有填钩子"),
        "开头没接钩子": ("catch", "没有接住"),
        "伏笔超期": ("threads", "已隔"),
        "信息差倒退": ("knowledge", "已经知道"),
        "写手不一致": ("batch", "只有一个写手"),
        "没加载最新正典": ("batch", "正典指纹"),
        "道具账对不上": ("delta", "账上在"),
        "未知人物 id": ("delta", "nina"),
    }
    for name, (check, frag) in wanted.items():
        expect("查出：" + name, any(c == check and frag in m for c, m in msgs), out if not msgs else "")
    code, out = run("merge", "--project", project, "--agent", "keeper-c")
    expect("有冲突时拒绝合并", code == 1 and not os.path.exists(os.path.join(project, "state", "ledger.json")), out)


def scaffold(tmp, name, style, platform, mode="new"):
    project = os.path.join(tmp, name)
    run("init", project, "--mode", mode, "--style", style, "--platform", platform)
    return project


def overrides(project, **extra):
    path = os.path.join(project, "project.json")
    cfg = cws.read_json(path)
    cfg.update(extra)
    cws.write_json(path, cfg)


def test_styles(tmp):
    cases = [
        ("cn-webnovel", "cn-serial", "第1章 账\n\n他极其愤怒。\n\n他说：你走。\n\n「站住。」\n\n一切才刚刚开始。\n",
         ["极其", "丢了引号", "直角引号", "总结句"], "第1章 账\n\n沈青禾把账册合上。\n\n“先生的袖子，”她说，“该换了。”\n\n门外有人敲了三下。\n"),
        ("en-romcom", "en-app-serial", "He gave a predatory grin.\n\nIt was only the beginning.\n",
         ["predatory", "总结句"], "“Line four,” she said.\n\nHis phone rang.\n"),
        ("en-dark-romance", "kindle-ku", "His obsidian eyes burned.\n\nNothing would ever be the same.\n",
         ["obsidian", "总结句"], "“Two tickets,” he said.\n\nThe car was already running.\n"),
        ("drama-script", "short-drama", "第1集\n\n△ 他心想该走了。\n",
         ["心想", "场次标题", "对白行"], "第1集\n\n1-1 夜 内 走廊\n△ 林夏攥着手机。\n林夏：他叫我什么？\n周警官：你没听错。\n林夏：再说一遍。\n"),
    ]
    for style, platform, bad, frags, good in cases:
        project = scaffold(tmp, style, style, platform)
        overrides(project, overrides={"length": {"min": 1, "max": 5000}})
        write(project, "chapters/ch-001.md", bad)
        _, out = run("check", "--project", project, "--only", "banned,quotes,ending", "--json")
        msgs = " ".join(i["message"] for i in json.loads(out)["items"])
        for frag in frags:
            expect("%s 查出 %s" % (style, frag), frag in msgs, msgs)
        write(project, "chapters/ch-001.md", good)
        code, out = run("check", "--project", project, "--only", "banned,quotes,ending")
        expect("%s 干净样章通过" % style, code == 0, out)
    style_scoped = scaffold(tmp, "scoped", "en-romcom", "en-app-serial")
    overrides(style_scoped, overrides={"length": {"min": 1, "max": 5000}})
    write(style_scoped, "chapters/ch-001.md", "他极其愤怒。\n")
    code, _ = run("check", "--project", style_scoped, "--only", "banned")
    expect("中文词表不约束英文风格", code == 0)


def test_cjk_names(tmp):
    project = scaffold(tmp, "names", "cn-webnovel", "cn-serial")
    cws.write_json(os.path.join(project, "canon", "characters.json"), {"characters": [
        {"id": "a", "name": "李四海", "deprecated_names": ["李四"], "former_names": [{"name": "阿海", "chapters": "1"}]}]})
    write(project, "chapters/ch-001.md", "李四海进了门。阿海是他的小名。\n")
    write(project, "chapters/ch-002.md", "阿海又来了。李四也来了。\n")
    _, out = run("check", "--project", project, "--only", "names", "--json")
    items = json.loads(out)["items"]
    expect("现用名里的子串不误报", not any(i["chapter"] == 1 for i in items), out)
    expect("曾用名超范围报错", any(i["chapter"] == 2 and "曾用名" in i["message"] for i in items), out)
    expect("废弃名报错", any(i["chapter"] == 2 and "废弃名" in i["message"] for i in items), out)


def test_modes(tmp):
    project = scaffold(tmp, "m-new", "en-romcom", "en-app-serial", "new")
    code, out = run("gate", "--project", project, "--stage", "plan")
    expect("新书模式：地基未填时门禁拦下", code == 1 and "CWS:UNFILLED" in out, out)

    project = scaffold(tmp, "m-rw", "en-romcom", "en-app-serial", "rewrite")
    code, out = run("gate", "--project", project, "--stage", "plan")
    expect("改写模式：说明未填时拦下", code == 1 and "rewrite-brief" in out, out)
    expect("改写模式不要求情绪地图", "emotion-map" not in out, out)
    expect("改写模式没有生成情绪地图", not os.path.exists(os.path.join(project, "docs", "00-emotion-map.md")))
    write(project, "docs/rewrite-brief.md", "改写第 6–8 章。\n")
    shutil.copy(os.path.join(EXAMPLE, "canon", "characters.json"), os.path.join(project, "canon", "characters.json"))
    overrides(project, scope="6-8")
    code, out = run("gate", "--project", project, "--stage", "plan")
    expect("改写模式：正典和说明就绪即通过", code == 0, out)

    project = scaffold(tmp, "m-cont", "en-romcom", "en-app-serial", "continue")
    write(project, "docs/continuation-brief.md", "接第 3 章。\n")
    shutil.copy(os.path.join(EXAMPLE, "canon", "characters.json"), os.path.join(project, "canon", "characters.json"))
    shutil.copy(os.path.join(EXAMPLE, "canon", "threads.json"), os.path.join(project, "canon", "threads.json"))
    overrides(project, scope="4-6")
    code, out = run("gate", "--project", project, "--stage", "plan")
    expect("续写模式：没有已有正文时拦下", code == 1 and "已有正文" in out, out)
    write(project, "chapters/ch-003.md", "“Hi,” she said.\n")
    code, out = run("gate", "--project", project, "--stage", "plan")
    expect("续写模式：有正文就通过", code == 0, out)

    project = scaffold(tmp, "keep", "en-romcom", "en-app-serial")
    write(project, "project.json", '{"mode": "rewrite", "style": "cn-webnovel", "platform": "cn-serial"}\n')
    run("init", project, "--mode", "new")
    expect("init 不覆盖已有文件", cws.read_json(os.path.join(project, "project.json"))["mode"] == "rewrite")

    code = cws.main(["check", "--project", os.path.join(tmp, "does-not-exist")])
    expect("配置错误退出码 2", code == 2)


def test_hook_hardening(tmp):
    # 1. 付费点禁止使用软钩（如 button 或 question）
    project = os.path.join(tmp, "hook-paywall-soft")
    shutil.copytree(EXAMPLE, project)
    plan_path = os.path.join(project, "plan", "chapters.json")
    plan = cws.read_json(plan_path)
    plan["chapters"][2]["hook"]["type"] = "button"
    cws.write_json(plan_path, plan)
    code, out = run("check", "--project", project, "--only", "hooks")
    expect("查出：付费点禁止使用软钩 button", code == 1 and "付费点章节禁止使用软钩类型“button”" in out, out)

    # 2. 平台禁用类型（short-drama 禁用 button）
    project = os.path.join(tmp, "hook-drama-disallowed")
    shutil.copytree(EXAMPLE, project)
    p_cfg_path = os.path.join(project, "project.json")
    p_cfg = cws.read_json(p_cfg_path)
    p_cfg["platform"] = "short-drama"
    cws.write_json(p_cfg_path, p_cfg)
    plan_path = os.path.join(project, "plan", "chapters.json")
    plan = cws.read_json(plan_path)
    plan["chapters"][0]["hook"]["type"] = "button"
    cws.write_json(plan_path, plan)
    code, out = run("check", "--project", project, "--only", "hooks")
    expect("查出：平台禁用钩子类型 button", code == 1 and "平台 short-drama 禁止使用钩子类型“button”" in out, out)

    # 3. 单章强度低于平台下限告警
    project = os.path.join(tmp, "hook-weak-warn")
    shutil.copytree(EXAMPLE, project)
    plan_path = os.path.join(project, "plan", "chapters.json")
    plan = cws.read_json(plan_path)
    plan["chapters"][0]["hook"]["strength"] = 2
    cws.write_json(plan_path, plan)
    code, out = run("check", "--project", project, "--only", "hooks")
    expect("查出：单章强度低于平台下限告警", "低于平台下限 3" in out, out)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    tmp = tempfile.mkdtemp(prefix="cws-selftest-")
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            test_clean(tmp)
            test_broken(tmp)
            test_styles(tmp)
            test_cjk_names(tmp)
            test_modes(tmp)
            test_hook_hardening(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%s" % ("全部通过" if not failures else "失败 %d 项：%s" % (len(failures), "、".join(failures))))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
