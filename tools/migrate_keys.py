#!/usr/bin/env python3
"""把旧版汉化文件按上游的键名迁移规则搬到目标版本上。

用法:
    python3 tools/migrate_keys.py --old <旧zh_cn.json> --mc 1.21.1

产出(默认写到 .work/):
    base_<mc>.json   基准汉化: 键名未变的直接命中 + 按规则改名后命中的
    todo_<mc>.json   待翻译: 目标版本有、基准里没有的键(带英文原文)
    old_dead_<mc>.json  旧文件里已经彻底用不上的键(留档备份)

迁移规则来自上游 xaero.pac...io.serialization.updater.PlayerConfigTransformers:
    claims.protection.fromXxx          -> claims.protection.exceptions.xxx
    claims.protection.XFromY           -> claims.protection.exceptions.XByY
    claims.protection.exceptionGroups.X -> claims.protection.exceptions.groups.X
    claims.protection.fromParty        -> claims.protection.exceptions.fullAccess
同时处理 gui.xaero_pac_player_config_ 和 ..._tooltip_ 两个前缀。
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, ".work")
NAME = "gui.xaero_pac_player_config_"
TIP = "gui.xaero_pac_player_config_tooltip_"
PROT = "playerConfig.claims.protection."
GRP = "playerConfig.claims.protection.exceptionGroups."


def migrate_key(key):
    """返回迁移后的键, 不需要迁移则返回 None。"""
    for prefix in (TIP, NAME):
        if not key.startswith(prefix):
            continue
        opt = key[len(prefix):]
        if opt.startswith(GRP):
            return prefix + "playerConfig.claims.protection.exceptions.groups." + opt[len(GRP):]
        if opt.startswith(PROT):
            rest = opt[len(PROT):]
            if "." in rest:
                return None
            if opt == "playerConfig.claims.protection.fromParty":
                return prefix + "playerConfig.claims.protection.exceptions.fullAccess"
            if rest.startswith("from"):
                new = rest[4:5].lower() + rest[5:]
            else:
                new = rest.replace("From", "By")
            return prefix + "playerConfig.claims.protection.exceptions." + new
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True)
    ap.add_argument("--mc", default="1.21.1")
    ap.add_argument("--upstream", default=None)
    args = ap.parse_args()

    up_path = args.upstream or os.path.join(ROOT, "upstream", "en_us_%s.json" % args.mc)
    with open(up_path, encoding="utf-8") as f:
        en = json.load(f, strict=False)
    with open(args.old, encoding="utf-8") as f:
        old = json.load(f, strict=False)

    target = list(en)
    tset = set(target)

    # 1) 直接命中
    base = {}
    used_old = set()
    for k in target:
        if k in old:
            base[k] = old[k]
            used_old.add(k)

    # 2) 改名命中
    migrated = {}
    for k, v in old.items():
        nk = migrate_key(k)
        if nk and nk in tset and nk not in base:
            base[nk] = v
            migrated[k] = nk
            used_old.add(k)

    # 3) 按英文原文找回旧译文(用旧版 en 做对照),仅作为参考建议
    old_en_path = os.path.join(ROOT, "upstream", "en_us_1.21.3.json")
    suggestion = {}
    if os.path.exists(old_en_path):
        with open(old_en_path, encoding="utf-8") as f:
            old_en = json.load(f, strict=False)
        by_text = {}
        for k, v in old_en.items():
            if k in old:
                by_text.setdefault(v, []).append(k)
        for k in target:
            if k in base:
                continue
            hits = by_text.get(en[k])
            if hits:
                suggestion[k] = {"from": hits[0], "text": old[hits[0]]}

    todo = {k: en[k] for k in target if k not in base}
    dead = {k: v for k, v in old.items() if k not in used_old}

    os.makedirs(WORK, exist_ok=True)

    def dump(name, data):
        p = os.path.join(WORK, name)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent="\t")
            f.write("\n")
        print("  %-28s %4d 条  %s" % (name, len(data), p))

    print("上游 %s: 目标键 %d" % (args.mc, len(target)))
    dump("base_%s.json" % args.mc, base)
    dump("todo_%s.json" % args.mc, todo)
    dump("suggest_%s.json" % args.mc, suggestion)
    dump("old_dead_%s.json" % args.mc, {k: old[k] for k in old if k not in used_old})

    print("\n复用 %d 条 (直接 %d, 改名 %d), 待翻译 %d 条, 旧文件无用 %d 条, 原文匹配建议 %d 条"
          % (len(base), len(target) - len(todo) - len(migrated), len(migrated),
             len(todo), len(dead), len(suggestion)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
