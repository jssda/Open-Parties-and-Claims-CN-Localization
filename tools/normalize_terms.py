#!/usr/bin/env python3
"""按术语表统一 zh_cn.json 的用词, 并清理空白噪声。

用法:
    python3 tools/normalize_terms.py --mc 1.21.1            # 就地统一
    python3 tools/normalize_terms.py --mc 1.21.1 --check    # 只报告不修改(有残留退出码 1)

规则表见 docs/glossary.md, 需要改口径时两边一起改。
空白清理会参考上游英文: 上游自己带前后空白/换行的条目不动译文格式。
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZH = os.path.join(ROOT, "assets", "openpartiesandclaims", "lang", "zh_cn.json")

# (正则, 替换) —— 统一口径, 顺序敏感
RULES = [
    (r"与你同队伍的", "与你同一团队的"),
    (r"同队伍", "同一团队"),
    (r"队友", "团队成员"),
    (r"队伍", "团队"),
    (r"(?<!共)同盟", "盟友"),   # "共同盟友" 不能动
    (r"声明", "占领"),
    (r"(?<=[\u4e00-\u9fff]):", "："),   # 中文后的半角冒号
    (r"挖掘问例外", "挖掘例外"),          # 旧译文笔误
]

# 只用于 --check 提示: 不应该再出现的旧用词
BANNED = ["声明", "队伍", "队友"]

# 空白噪声清理
WS_RULES = [
    (r" {2,}", " "),          # 连续空格
    (r"\n[ \t]+", "\n"),      # 行首缩进
    (r"[ \t]+\n", "\n"),      # 行尾空格
    (r"\n{3,}", "\n\n"),      # 多余空行
]


def tidy_ws(v, en_val):
    for pat, rep in WS_RULES:
        if pat == r" {2,}" and "  " in en_val:
            continue
        if pat in (r"\n[ \t]+", r"[ \t]+\n") and re.search(r"\n[ \t]", en_val):
            continue
        if pat == r"\n{3,}" and "\n\n\n" in en_val:
            continue
        v = re.sub(pat, rep, v)
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", default="1.21.1")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    en_path = os.path.join(ROOT, "upstream", "en_us_%s.json" % args.mc)
    with open(en_path, encoding="utf-8") as f:
        en = json.load(f, strict=False)
    with open(ZH, encoding="utf-8") as f:
        data = json.load(f)

    hits = {}
    ws_hits = []
    for k, v in data.items():
        for pat, rep in RULES:
            nv = re.sub(pat, rep, v)
            if nv != v:
                hits.setdefault(pat, []).append(k)
                v = nv
        tidied = tidy_ws(v, en.get(k, ""))
        if tidied != v:
            ws_hits.append(k)
        data[k] = tidied

    print("术语命中:")
    for pat, rep in RULES:
        print("  %-16s -> %-14s %d 条" % (pat, rep, len(hits.get(pat, []))))
    print("空白清理: %d 条" % len(ws_hits))

    left = []
    for k, v in data.items():
        for b in BANNED:
            if b in v:
                left.append((k, b, v[:60]))
        if re.search(r" {2,}|\n[ \t]", v) and "  " not in en.get(k, ""):
            left.append((k, "空白", v[:60]))

    if args.check:
        if left:
            print("\n仍有问题 %d 条:" % len(left))
            for k, b, v in left[:20]:
                print("   [%s] %s | %s" % (b, k, v))
            return 1
        print("\n术语与空白检查通过")
        return 0

    with open(ZH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent="\t")
        f.write("\n")
    print("\n已写回 %s" % ZH)
    if left:
        print("注意: 仍有 %d 条存在问题(可能是新加的译文), 请手动确认" % len(left))
    return 0


if __name__ == "__main__":
    sys.exit(main())
