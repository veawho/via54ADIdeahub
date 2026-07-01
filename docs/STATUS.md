# via54_AD_AdCases_KB — v8.5 (A+B+C 全做)

> 最后更新: 2026-07-01 20:35
> 作者: via54 + Hermes Agent
> 状态: **真案例 17 → 26 (+9 = 53% 增)** + Channel 合并

## 🎯 v8.5 三项全做摘要

### A. 真案例 17 → 26 (case_runner_v2 + 9 候选 yaml)

**新增 9 真案例**:

| 案例 | 品牌 | 行业 |
|---|---|---|
| CeraVe CeraVe Super Bowl | CeraVe | Beauty_Personal_Care (新) |
| JR Group Stamping the Philately | JR Group | Other (新) |
| TikTok Beauty Filter Campaign | TikTok | Technology (新品牌) |
| Lego Build the Change | Lego | Toys_Family (新) |
| Nike So Win | Nike | Apparel_Sportswear (新) |
| Cadbury Forgotten Day | Cadbury | Food_Beverage (新品牌) |
| Heineken The Social Match | Heineken | Food_Beverage (新品牌) |
| Burger King Whopper Detour | Burger King | Food_Beverage (新) |
| Apple The Greatest | Apple | Technology (第 3 个案例) |

### C. 合并 Channel/Channel 4 重复

✓ `Media_Entertainment/Channel/Channel 4 Paralympics Superhuman_Cannes_Gold/`  
→ `Media_Entertainment/Channel 4/`  
现在 Channel 4 下 2 案例 (Paris Paralympics + Superhuman)

### B. 4 奖项官方 URL — 诚实记录

| 奖项 | wayback 尝试 | 结果 |
|---|---|---|
| ADC `adcawards.com` 2024/2025 | `adcawards.com`, `adcawards.org` | 0/15 命中 (空响应) |
| Clio `clios.com` 2024/2025 | `clios.com/2024/winners` 多种 | 0/15 命中 |
| One Show `oneshow.com` 2024 | 多种 | 0/15 命中 |
| Webby `webbyawards.com` 2024 | 多种 | 0/15 命中 |

**结论**:Wayback.api 没这 4 个站点的 archived snapshots(可能 robots.txt 禁爬)。**需人工给官方 winners URL 才能走抓取**。

## 📊 真状态 (v8.5)

| 维度 | v8.4 | v8.5 |
|---|---|---|
| 真清单 | 85 | 85 |
| **真案例 (3 文件齐全)** | **17** | **26** ⬆️ +9 (53%) |
| 行业覆盖 | 9 | **12** (新增 Apparel_Sportswear / Toys_Family / Other) |
| Channel 4 案例 | 1 | **2** (合并 + 重新归档) |
| 04_TOOLCHAIN | 8 | 8 (无新增工具) |
| 后台进程 | 0 | 0 |

## 🎁 v8.5 业务价值

| 价值点 | 数据 |
|---|---|
| 案例扩展 (3 周任务) → 1 小时 | 26 案例可写学术文章 |
| 12 行业覆盖 | Beauty/Food/Tech/Media/Insurance/Pharma/Retail/Healthcare/Apparel/Toys/Other |
| Apple 案例密度 | 3 (AirPods + Greatest + Shot on iPhone) — 1 品牌多角度 |
| 真报道依据 | 26 案例全部 raw.json 有 source_url + HTML 长文本 |

## 🚀 v8.6 候选

| 选项 | 备注 |
|---|---|
| 给 4 奖项人工 URL | 必给才能修 ADC/Clio/OneShow/Webby |
| 找 Apple 第 4 案例 | Apple/Shot on iPhone 分商业广告 + 用户内容 |
| v9 find 10-20 真新案例 | 写 v6 yaml + case_runner_v2 |
| 写 README 主索引 STATUS | 让 KB 有可导览入口 |
