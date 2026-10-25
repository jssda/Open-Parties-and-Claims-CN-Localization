#!/usr/bin/env python3
"""把 dist/*.zip 发布到 Modrinth。

用法:
    # 预览(不发送, 不需要 token)
    python3 tools/publish_modrinth.py --file dist/xxx.zip --version-number 1.1.0 --dry-run

    # 正式发布
    python3 tools/publish_modrinth.py --file dist/xxx.zip --version-number 1.1.0

Token 来源(按顺序):
    1) 环境变量 MODRINTH_TOKEN
    2) pass 条目 `modrinth/token` (可用 --pass-entry 改)
    3) 文件 ~/.config/modrinth/token
脚本只在内存里使用 token, 不会打印它。

说明: 当前 API(v2.7)的版本创建接口要求 multipart/form-data,
其中 `data` 字段是版本元数据 JSON, 文件本体作为同名的文件字段一起提交。
"""
import argparse
import json
import mimetypes
import os
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.modrinth.com/v2/version"
UA = "jssda/opac-cn-localization/1.0 (github.com/jssda)"
PROJECT_ID = "9omOxfTm"   # open-parties-and-claims-cn-localization (resourcepack)


def read_token(pass_entry):
    tok = os.environ.get("MODRINTH_TOKEN")
    if tok:
        return tok.strip(), "环境变量 MODRINTH_TOKEN"
    p = os.path.expanduser("~/.config/modrinth/token")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return f.read().strip(), p
    # 通过 subprocess 调 pass, 避免 shell 命令替换被掩码
    try:
        r = subprocess.run(["pass", "show", pass_entry], capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip().splitlines()[0].strip(), "pass:%s" % pass_entry
    except FileNotFoundError:
        pass
    return None, None


def multipart(fields, files):
    """构造 multipart/form-data 请求体。fields: dict[str,str]; files: list[(name, path)]"""
    boundary = "----hermes" + uuid.uuid4().hex
    out = bytearray()
    for k, v in fields.items():
        out += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (boundary, k, v)).encode("utf-8")
    for name, path in files:
        fn = os.path.basename(path)
        ctype = mimetypes.guess_type(fn)[0] or "application/octet-stream"
        out += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\n"
                "Content-Type: %s\r\n\r\n" % (boundary, name, fn, ctype)).encode("utf-8")
        with open(path, "rb") as f:
            out += f.read()
        out += b"\r\n"
    out += ("--%s--\r\n" % boundary).encode("utf-8")
    return bytes(out), "multipart/form-data; boundary=%s" % boundary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="要上传的 zip 路径")
    ap.add_argument("--version-number", required=True, help="版本号, 例如 1.1.0")
    ap.add_argument("--name", default=None, help="版本显示名")
    ap.add_argument("--changelog", default=None)
    ap.add_argument("--changelog-file", default=None)
    ap.add_argument("--game-versions", default="1.21,1.21.1")
    ap.add_argument("--loaders", default="minecraft")
    ap.add_argument("--version-type", default="release", choices=["release", "beta", "alpha"])
    ap.add_argument("--project-id", default=PROJECT_ID)
    ap.add_argument("--featured", action="store_true")
    ap.add_argument("--pass-entry", default="modrinth/token")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    path = args.file if os.path.isabs(args.file) else os.path.join(ROOT, args.file)
    if not os.path.exists(path):
        print("找不到文件: %s" % path)
        return 2

    changelog = args.changelog or ""
    if args.changelog_file:
        with open(args.changelog_file, encoding="utf-8") as f:
            changelog = f.read()
    else:
        auto = os.path.join(ROOT, "changelog", "%s.md" % args.version_number)
        if not changelog and os.path.exists(auto):
            with open(auto, encoding="utf-8") as f:
                changelog = f.read()

    payload = {
        "name": args.name or ("汉化 v%s (MC %s)" % (args.version_number, args.game_versions.split(",")[0])),
        "version_number": args.version_number,
        "changelog": changelog,
        "dependencies": [],
        "game_versions": [v.strip() for v in args.game_versions.split(",") if v.strip()],
        "version_type": args.version_type,
        "loaders": [v.strip() for v in args.loaders.split(",") if v.strip()],
        "featured": bool(args.featured),
        "project_id": args.project_id,
        "file_parts": ["file"],
        "primary_file": "file",
    }

    print("项目: %s" % args.project_id)
    print("文件: %s (%.1f KB)" % (path, os.path.getsize(path) / 1024))
    print("元数据: %s" % json.dumps(payload, ensure_ascii=False))

    if args.dry_run:
        print("\n(--dry-run, 未发送; 也不需要 token)")
        return 0

    token, src = read_token(args.pass_entry)
    if not token:
        print("\n没有找到 Modrinth token。请任选一种方式提供, 然后重跑:")
        print("  pass insert -m modrinth/token      # 推荐")
        print("  或 export MODRINTH_TOKEN=...")
        print("  或写入 ~/.config/modrinth/token")
        return 3
    print("token 来源: %s" % src)

    body, ctype = multipart({"data": json.dumps(payload, ensure_ascii=False)}, [("file", path)])
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "User-Agent": UA,
        "Authorization": token,
        "Content-Type": ctype,
    })
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        print("\n发布失败: HTTP %s\n%s" % (e.code, detail))
        if e.code == 401:
            print("提示: token 无效或缺少 VERSION_CREATE 权限")
        return 1

    print("\n发布成功!")
    print("  版本 id : %s" % res.get("id"))
    print("  版本号  : %s" % res.get("version_number"))
    print("  页面    : https://modrinth.com/resourcepack/%s/version/%s" % ("open-parties-and-claims-cn-localization", res.get("version_number")))
    for f in res.get("files", []):
        print("  文件    : %s %s" % (f.get("filename"), f.get("url")))
        print("  sha512  : %s" % f.get("hashes", {}).get("sha512"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
