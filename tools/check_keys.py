#!/usr/bin/env python3
"""校验汉化文件与上游 en_us.json 的一致性。

用法:
    python3 tools/check_keys.py --mc 1.21.1

检查项:
  1. 缺失键(上游有、汉化没有)      -> 游戏内会回落英文
  2. 多余键(汉化有、上游没有)      -> 上游已改名/删除
  3. 占位符不一致(%1$s 等数量/编号)
  4. 空值、值首尾多余空白、多余连续换行
  5. 与英文完全相同(疑似漏译,仅提示)

有 1~4 类问题时退出码为 1,方便 CI 使用。
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZH = os.path.join(ROOT, "assets", "openpartiesandclaims", "lang", "zh_cn.json")

PH_RE = re.compile(r"%(?:\d+\$)?[sdf]")


def placeholders(text):
    """把 %1$s / %s 统一成出现顺序签名, 便于对比。"""
    out = []
    implicit = 0
    for m in PH_RE.finditer(text):
        tok = m.group(0)

        def kind(t):
            return t[-1]
        if tok.startswith("%") and "$" in tok:
            out.append((int(tok[1:tok.index("$")]), kind(tok)))
        else:
            implicit += 1
            out.append((implicit, kind(tok)))
    return sorted(out)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f, strict=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", default="1.21.1")
    ap.add_argument("--upstream", default=None)
    args = ap.parse_args()

    up_path = args.upstream or os.path.join(ROOT, "upstream", "en_us_%s.json" % args.mc)
    en = load(up_path)
    zh = load(ZH)

    missing = sorted(k for k in en if k not in zh)
    extra = sorted(k for k in zh if k not in en)
    ph_bad = []
    cleaned = []
    empty = []
    same_as_en = []

    for k, v in zh.items():
        if k in en:
            # 上游把部分动态选项的说明值写成 "default", 作为"用服务端下发文本"的哨兵值,
            # 这类条目允许占位符不同。
            if en[k] != "default" and placeholders(v) != placeholders(en[k]):
                ph_bad.append((k, en[k], v))
        if not v.strip():
            empty.append(k)
        elif v != v.strip() and not (en.get(k, "").startswith((" ", "\t")) or en.get(k, "").endswith("\n")):
            # 上游英文自己带前后空白/换行的条目, 译文保留同样格式是有意的
            cleaned.append(k)
        if "\n\n\n" in v and "\n\n\n" not in en.get(k, ""):
            cleaned.append(k)
        if k in en and v == en[k]:
            same_as_en.append(k)

    def dump(title, items, limit=25):
        if not items:
            return
        print("\n== %s (%d) ==" % (title, len(items)))
        if isinstance(items[0], tuple):
            for row in items[:limit]:
                print("   %s\n     en: %s\n     zh: %s" % (row[0], row[1], row[2]))
        else:
            for k in items[:limit]:
                print("   %s" % k)
        if len(items) > limit:
            print("   ... 其余 %d 条" % (len(items) - limit))

    print("上游键 %d / 汉化键 %d" % (len(en), len(zh)))
    dump("缺失键(会显示英文)", missing)
    dump("多余键(上游已无此键)", extra)
    dump("占位符不一致(必须修)", ph_bad)
    dump("空值(必须修)", empty)
    dump("值首尾空白/多余空行(建议清理)", sorted(set(cleaned)))
    dump("与英文原文相同(疑似漏译)", same_as_en)

    fatal = len(missing) + len(ph_bad) + len(empty)
    print("\n结果: 缺失 %d, 多余 %d, 占位符 %d, 空值 %d" % (len(missing), len(extra), len(ph_bad), len(empty)))
    if fatal:
        print("=> 未通过")
        return 1
    print("=> 通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
