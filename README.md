# Open-Parties-and-Claims-CN-Localization

[Open Parties and Claims](https://modrinth.com/mod/open-parties-and-claims)（作者 Xaero96）的简体中文汉化**资源包**。

Modrinth: <https://modrinth.com/resourcepack/open-parties-and-claims-cn-localization>

- 汉化方式：资源包只放语言文件（`assets/openpartiesandclaims/lang/zh_cn.json`），不改动模组本体；资源包优先级高于模组内置资源，装包即生效。
- 支持加载器：NeoForge / Forge / Fabric 均可（与加载器无关）。
- 翻译：早期为 DeepSeek 初翻 + 手动修正，当前版本按上游最新语言文件逐条核对、迁移与重译。

## 版本对照

| 汉化版本 | 对应模组版本 | Minecraft | 资源包 pack_format |
|---|---|---|---|
| v0.33.0+mc1.21.1 | 0.33.0 | 1.21 / 1.21.1 | 34 |
| v0.24.2（旧版，已过时） | 0.24.2 | 1.21–1.21.5 | 46（声明支持 34–46） |

> 当前版本只声明 `pack_format: 34`（= 1.21 / 1.21.1）。换到别的 MC 版本时游戏会提示"为不同版本制作"，但更关键的是**键名对不上**，配置界面的选项会回落英文——所以请按下文"更新到新版本"重新出一份，别直接复用。

> 模组不同 MC 分支的版本号与**语言键名**都不一样（例如配置选项从 `claims.protection.blocksFromPlayers` 改成 `claims.protection.exceptions.blocksByPlayers`），所以每个 MC 版本要单独做一份。换 MC 版本请按下面"更新到新版本"走一遍。

## 安装

把 `dist/Open-Parties-and-Claims-CN-v0.33.0+mc1.21.1.zip` 放进 `.minecraft/resourcepacks/`，在游戏里"选项 → 资源包"启用（游戏语言需为**简体中文**）。

服务器提示：给**未安装该模组**的客户端（原版客户端）发的消息由服务端预翻译。若想让这些消息也是中文，需要把 `zh_cn.json` 以数据包形式放进存档的 `data/openpartiesandclaims/lang/` 目录，或把模组服务器配置里的 `defaultLanguage` 设为 `zh_cn`。

## 仓库结构

```
pack.mcmeta                     # 资源包描述(pack_format 34)
pack.png                        # 资源包图标
assets/openpartiesandclaims/lang/zh_cn.json   # 唯一需要维护的翻译文件
upstream/en_us_<mc>.json        # 上游基准语言文件(用于比对)
tools/fetch_upstream.py         # 从 Modrinth 拉取指定 MC 版本的最新 jar 并抽出 en_us.json
tools/check_keys.py             # 校验: 缺失键/多余键/占位符/空值/空白/疑似漏译
tools/migrate_keys.py           # 旧汉化文件按上游改名规则迁移到新版本(产出 .work/)
tools/compose.py                # 合成最终 zh_cn.json(基准 + 新译, 按上游键序)
tools/normalize_terms.py        # 术语与空白统一(规则见 docs/glossary.md)
tools/build.py                  # 打包 dist/*.zip
tools/publish_modrinth.py       # 发布到 Modrinth(令牌走 pass:modrinth/token, 支持 --dry-run)
changelog/<版本号>.md            # 该版本的更新说明(发布时自动带上)
docs/glossary.md                # 术语对照表
.github/workflows/release.yml   # 打 tag 自动校验 + 打包 + 发 Release
```

## 日常维护

```bash
# 1. 校验当前汉化与上游是否一致(上游更新后先跑这个)
python3 tools/fetch_upstream.py --mc 1.21.1
python3 tools/check_keys.py --mc 1.21.1

# 2. 术语与空白
python3 tools/normalize_terms.py --mc 1.21.1          # 就地统一
python3 tools/normalize_terms.py --mc 1.21.1 --check  # 只检查(CI 用)

# 3. 打包
python3 tools/build.py --mod-version 0.33.0 --mc 1.21.1
```

## 更新到新版本

```bash
# 1. 拉上游基准
python3 tools/fetch_upstream.py --mc <新MC版本>

# 2. 把现有译文按上游改名规则迁移, 产出 .work/base_*.json(可复用) 与 .work/todo_*.json(待翻译)
python3 tools/migrate_keys.py --old assets/openpartiesandclaims/lang/zh_cn.json --mc <新MC版本>

# 3. 人工翻译 .work/todo_*.json, 按批次写成 .work/new_<mc>_*.json(键 → 译文)

# 4. 合成 → 统一术语 → 校验
python3 tools/compose.py --mc <新MC版本>
python3 tools/normalize_terms.py --mc <新MC版本>
python3 tools/check_keys.py --mc <新MC版本>

# 5. 改 pack.mcmeta 的 pack_format / 描述, 打包
python3 tools/build.py --mod-version <模组版本> --mc <新MC版本>
```

发布：给 commit 打 tag（格式 `v<模组版本>+mc<MC版本>`，如 `v0.33.0+mc1.21.1`）并推送，CI 会自动校验、打包并发 Release；Modrinth 目前需手动上传 `dist/*.zip`。

## 参与

发现翻译错误或漏译，欢迎提 Issue / PR。提 PR 前请先跑一遍 `check_keys.py` 与 `normalize_terms.py --check`。

## 许可

MIT（见 LICENSE）。模组本体及其语言文件版权归 Xaero96 所有。
