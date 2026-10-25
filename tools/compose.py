#!/usr/bin/env python3
"""合成最终 zh_cn.json: .work/base_<mc>.json + .work/new_<mc>*.json

用法:
    python3 tools/compose.py --mc 1.21.1
    python3 tools/compose.py --mc 1.21.1 --check

按上游 en_us.json 的键顺序输出,顺手做值清理(首尾空白、3 个以上连续换行),
并校验占位符,有问题直接报错不写文件。
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, ".work")
OUT = os.path.join(ROOT, "assets", "openpartiesandclaims", "lang", "zh_cn.json")
PH_RE = re.compile(r"%(?:\d+\$)?[sdf]")


def placeholders(text):
    out = []
    implicit = 0
    for m in PH_RE.finditer(text):
        tok = m.group(0)
        if "$" in tok:
            out.append((int(tok[1:tok.index("$")]), tok[-1]))
        else:
            implicit += 1
            out.append((implicit, tok[-1]))
    return sorted(out)


def clean(text, en_text):
    """清理译文里 DeepSeek 时代留下的空白噪声, 但上游自己带前后空白/换行的条目保持原样。"""
    if not en_text.startswith((" ", "\t")):
        text = text.lstrip(" \t")
    if not en_text.endswith("\n"):
        text = text.rstrip(" \t\n")
    if "\n\n\n" not in en_text:
        text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", default="1.21.1")
    ap.add_argument("--check", action="store_true", help="只校验不写文件")
    args = ap.parse_args()

    with open(os.path.join(ROOT, "upstream", "en_us_%s.json" % args.mc), encoding="utf-8") as f:
        en = json.load(f, strict=False)

    merged = {}
    for path in sorted(glob.glob(os.path.join(WORK, "base_%s.json" % args.mc))) + \
            sorted(glob.glob(os.path.join(WORK, "new_%s*.json" % args.mc))):
        with open(path, encoding="utf-8") as f:
            part = json.load(f, strict=False)
        overlap = set(part) & set(merged)
        if overlap:
            print("警告: %s 覆盖了 %d 条已有译文" % (os.path.basename(path), len(overlap)))
        merged.update(part)
        print("载入 %-24s %4d 条" % (os.path.basename(path), len(part)))

    out = {}
    problems = []
    for k in en:
        if k not in merged:
            continue
        v = clean(merged[k], en[k])
        if not v:
            problems.append("空值: %s" % k)
            continue
        if en[k] != "default" and placeholders(v) != placeholders(en[k]):
            problems.append("占位符不一致: %s\n    en: %s\n    zh: %s" % (k, en[k], v))
            continue
        out[k] = v

    missing = [k for k in en if k not in out]
    extra = [k for k in merged if k not in en]

    print("\n目标键 %d, 已覆盖 %d, 缺失 %d, 多余 %d" % (len(en), len(out), len(missing), len(extra)))
    if missing:
        print("缺失键(最多列 30 条):")
        for k in missing[:30]:
            print("   %s" % k)
    if extra:
        print("多余键(最多列 30 条):")
        for k in extra[:30]:
            print("   %s" % k)
    if problems:
        print("\n问题 %d 条:" % len(problems))
        for p in problems[:30]:
            print("   %s" % p)
        return 1

    if args.check:
        print("(--check 模式, 未写文件)")
        return 0

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent="\t")
        f.write("\n")
    print("\n已写出 %s (%d 键, %.1f KB)" % (OUT, len(out), os.path.getsize(OUT) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
