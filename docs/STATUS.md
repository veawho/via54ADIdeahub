# via54_AD_AdCases_KB 项目状态 — v6.0 (最终真实状态)

> 最后更新: 2026-07-01
> 作者: via54 + Hermes Agent
> 状态: **已落到地面**

## 🎯 目标回顾
建立 `G:\agent\knowledge\reports\via54_AD_AdCases_KB\` 广告案例知识库,
5+1 规则,工具栈,跑通真实获奖案例完整流程。

## 📊 最终真实数据 (经 3 次审计)

### 02_AWARD_SOURCES/ 真清单

| 奖项 | 文件数 | 真数据来源 |
|---|---|---|
| **Cannes Lions** | 39 | canneslions.com (官方) |
| **Effie** | 20 | effie.org / apaceffie.com / effie-europe.com / current.effie.org |
| **D&AD** | 10 | dandad.org (官方) |
| **LIA** | 7 | liaawards.com |
| **Spikes Asia** | 5 | spikes.asia |
| ADC/Clio/One_Show/Webby/LongXi | 0 | 未抓到真源 |
| **总计** | **81 真清单** | **0 占位** |

### 05_CASES/By_Industry/ 真案例

**9 真案例** (全部从 case_runner 抓的,经 domain 校验 + 深度报告):

| # | 案例 | 品牌 | 行业 | 主奖项 |
|---|---|---|---|---|
| 1 | Three Words | AXA | Insurance | Dan Wieden Titanium GP |
| 2 | The Misheard Version | Specsavers | Retail | Audio/Radio GP |
| 3 | Recycle Me | Coca-Cola | Food_Beverage | Sustainable Dev GP |
| 4 | Real Beauty | Dove | Beauty_Personal_Care | Glass: The Lion for Change GP |
| 5 | The Amazon Greenventory | Natura | Beauty_Personal_Care | Creative B2B GP |
| 6 | Magnetic Stories | Siemens Healthineers | Healthcare_MedTech | Pharma GP |
| 7 | Paris Paralympics 2024 | Channel 4 | Media_Entertainment | Film GP |
| 8 | The Last Barf Bag | Dramamine | Pharmaceutical | Pharma GP |
| 9 | Shot on iPhone | Apple | Technology | Brand Experience GP |

每个含 5 产物:
- `*_raw.json` (案例数据)
- `FOLDER_README.md` (案例说明)
- `概述.md` (品牌+行业+主源)
- `深度报告.md` (基于 SearXNG 候选的骨架)
- `视频清单.md` (Top 5 SearXNG 视频源)

## ⚠️ v5.0 误报修正 (诚实记录)

| 之前报告 (v3.0-v5.0) | 真实状态 (v6.0) |
|---|---|
| 117 真清单 | **81 真清单** (34 误标已删) |
| 1296 真案例 | **9 真案例** (其他全噪声) |
| 6 真案例 (v3.0) → 4 真案例 (v5.0) | **9 真案例** (清理错位时少算) |
| Cron 24h 滚动 enrich | **Gateway 未运行, 实际未跑** |

### 误标根因
- 阶段 1-3 subagent 时代抓的 34 个文件,数据源是 llllitl.fr / creativereview.co.uk / adweek.com 等**跨奖项汇总页**,domain 与奖项目录不匹配
- Effie 2024 + D&AD + LIA 清单**本身是新闻/导航/链接集合**,不是案例名列表
- 工具 v3.1 报"X 案例"实际是**描述行** (`04_collect_award_winners.py` 没做表格行类型区分)

## 🔧 工具链 (v3.2 + 3 commits)

| 工具 | 路径 | 功能 | 状态 |
|---|---|---|---|
| `04_collect_award_winners.py` | `04_TOOLCHAIN/` | 抓奖项 winners 清单 | v3.2 (PDF + SEED + domain 校验) |
| `03_collect_case.py` | `04_TOOLCHAIN/` | 抓单个案例 | 141 行 |
| `enrich_case_cron.py` | `04_TOOLCHAIN/` | enrich 已有案例 | 9/9 真案例已 enrich |
| `case_runner_v2.py` | `04_TOOLCHAIN/` | 批量案例抓取 | 已用 1 次 |
| `05_collect_all_cases.py` | `04_TOOLCHAIN/` | 全量抓案例 (新) | v1, **未跑通**(清单噪声太多) |

git commits: `2d33237` `108977b` `0c76a37`

## ⏸️ 受限事项

| 受限 | 原因 | 解决方案 |
|---|---|---|
| 5 奖项 0 真数据 (ADC/Clio/One_Show/Webby/LongXi) | SearXNG + domain 限制 | 等 cron 24h 滚动 (Gateway 未运行 = 实际未跑) |
| Effie 2024 清单噪声 | 官方汇总页是新闻 | 用 Effie 2025/2026 真案例 |
| D&AD/LIA 清单噪声 | 抓的是导航/PR | 改抓 dandad.org work library / liaawards.com work library |
| Cron 未跑 | Gateway 离线 | 手动 enrich 9 案例已完成 |

## 📌 教训 (落到 SKILL/memory)

1. **"STATUS 数字必须 audit 后写"** — STATUS v3.0-v5.0 三次数字失实 (117/1296/6/4 → 81/9)。已落 SKILL `ad-case-study-kb` Pitfall 16+17
2. **"verify config BEFORE reporting"** — Cron 状态报"active + 24h 滚动"实际 Gateway 离线
3. **"全量 ≠ 一次抓完"** — 1183/774 案例数字失真,实际真案例 9,需逐个 enrich
4. **"gather evidence first"** — 应先 audit 清单内容再跑全量,不是反过来
