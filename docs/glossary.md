# 术语对照表

汉化统一口径。新增/修改译文时请照此办理；批量替换规则见 `tools/normalize_terms.py`（改口径时两处一起改）。

## 核心术语

| 英文 | 译名 | 说明 |
|---|---|---|
| party | 团队 | 不用"队伍""帮派" |
| party owner | 团队所有者 | |
| party member | 团队成员 | 不用"队友" |
| ally / allied party | 盟友 / 盟友团队 | 不用"同盟" |
| mutual ally parties | 互相结盟的团队 | "共同盟友"一词保留（与共同盟友共享位置） |
| claim（名词） | 领地 | |
| claim（动词） | 占领 | 不用"声明" |
| unclaim | 取消占领 | |
| chunk | 区块 | |
| claimed chunk | 已占领的区块 / 领地区块 | |
| wilderness | 荒野 | 未被任何人占领的区块 |
| claiming anchor | 领地锚点 | 动词场景区分 放置锚点 / 移除锚点 |
| anchor range | 锚点范围 | |
| forceload | 强制加载 | forceload-marked = 标记为强制加载；unforceload = 取消强制加载标记 |
| sub-config | 子配置 | |
| sub-claim | 子领地 | |
| player config | 玩家配置 | |
| player group | 玩家分组 | 空间 = group space |
| custom player groups | 自定义玩家分组 | |
| exception | 例外 | |
| exception group | 例外分组 | |
| protection | 保护 / 防护 | 选项名用"保护"，说明文字用"防护" |
| admin mode | 管理员模式 | |
| moderator mode | 审核模式 | |
| impersonate / impersonation | 代理 | "代理玩家""以对方身份操作" |
| transfer（claims） | 转让 | |
| clear（claims） | 清空 | 与"取消占领"区分 |
| teleport | 传送 | |
| dimension | 维度 | |
| source player | 来源玩家 | 指令上下文 |
| target player | 目标玩家 | |
| addon | 附加模组 | |
| interrupt | 中断 | |
| over-area claim action | 跨区域领地操作 | |
| mass-replacement | 批量替换 | |
| expired claims | 过期领地 | |
| spawner | 刷怪笼 | |
| raids | 袭击 | |
| tripwire | 绊线 | |
| pressure plate | 压力板 | |
| chorus fruit teleport | 紫颂果传送 | |
| frost walking | 冰霜行者 | |
| mob griefing rule | 生物破坏游戏规则 | |
| item toss / pickup | 丢弃 / 拾取物品 | |
| xp pickup | 经验拾取 | |
| redirect | 重定向 | |
| block / entity / player access | 方块 / 实体 / 玩家访问 | |
| hand interact | 空手交互 | |
| barrier | 屏障 | |
| source player context | 以来源玩家身份执行指令 | |

## 格式约定

- 保留 `%1$s`、`%2$s`、`%1$d` 等占位符的编号与顺序含义，不要重排编号（可调整位置，但编号必须仍指同一参数）。
- 保留原文里的 `\n`（游戏内换行），不要随意增删。
- 上游把少数动态选项的说明值写成 `default` 作为"改用服务端下发文本"的哨兵值；我们把这些条目翻成真正的中文（`tools/check_keys.py` 对这类条目跳过占位符比对）。
- 指令名与关键词保留英文：`/oclaims`、`/openpac-parties`、`confirm`、`anyway`、`main`、`keepInventory`、维度 ID（`minecraft:the_nether` 等）。
- 标点用全角（，。：！？），但 `(%1$s)` 这类参数括号保持半角。
- 中文后不使用半角冒号。
- 感叹号、问号与原文语气一致（原文 !/? 保留）。
