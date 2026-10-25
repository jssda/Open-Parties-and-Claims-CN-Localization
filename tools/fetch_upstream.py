#!/usr/bin/env python3
"""拉取上游 en_us.json 作为翻译基准。

用法:
    python3 tools/fetch_upstream.py --mc 1.21.1

做法: 用 Modrinth API 找到该 MC 版本最新的 (neo)forge jar,下载后
从 jar 内取出 assets/openpartiesandclaims/lang/en_us.json,
写到 upstream/en_us_<mc>.json。只依赖标准库。
"""
import argparse
import io
import json
import os
import sys
import urllib.request
import zipfile

MODRINTH = "https://api.modrinth.com/v2/project/open-parties-and-claims/version"
NS = "openpartiesandclaims"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "jssd/opac-cn-localization"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def find_jar(mc):
    versions = get_json(MODRINTH + "?game_versions=" + urllib.parse.quote(json.dumps([mc])))
    for v in versions:
        if "neoforge" not in v["loaders"]:
            continue
        for f in v["files"]:
            if f["filename"].endswith(".jar") and "sources" not in f["filename"]:
                return v["version_number"], f["url"]
    raise SystemExit("找不到 %s 对应的 jar" % mc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", default="1.21.1")
    args = ap.parse_args()

    version, url = find_jar(args.mc)
    print("mod 版本 %s -> %s" % (version, url))
    req = urllib.request.Request(url, headers={"User-Agent": "jssd/opac-cn-localization"})
    with urllib.request.urlopen(req, timeout=120) as r:
        blob = r.read()

    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        raw = z.read("assets/%s/lang/en_us.json" % NS)

    data = json.loads(raw.decode("utf-8"), strict=False)
    out = os.path.join(ROOT, "upstream", "en_us_%s.json" % args.mc)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent="\t")
        f.write("\n")
    print("已写入 %s (%d 键, mod %s)" % (out, len(data), version))


if __name__ == "__main__":
    import urllib.parse  # noqa: E402

    main()
