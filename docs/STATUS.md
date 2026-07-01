# via54_AD_AdCases_KB — v8.4 (修反爬 + 扩真案例)

> 最后更新: 2026-07-01 19:42
> 作者: via54 + Hermes Agent
> 状态: **真案例 9 → 17 (扩 8)**

## 🎯 v8.4 真实增量

### 真案例 9 → 17

| 增量 (8) | 来源 |
|---|---|
| Apple AirPods Pro 2 Hearing Aid | case_runner_v2 + batch_cases_v4.yaml |
| Dove Reverse Selfie | case_runner_v2 |
| Coca-Cola Master Plan | case_runner_v2 |
| Specsavers The Book of Dreams | case_runner_v2 |
| Natura Preservar | case_runner_v2 |
| AXA We Know Football | case_runner_v2 |
| Channel 4 Paralympics Superhuman | case_runner_v2 (归到 Channel/) |
| Dramamine Motion Sickness Patch | case_runner_v2 (Clio 不只 Cannes) |

### 工具改进

| 改进 | 文件 |
|---|---|
| `04_collect_award_winners.py` 多层 fallback (requests verify=False / WSL Chrome / wayback.archive.org) | v8.4 |
| `case_runner_v2.py` 接受 `--yaml` + `--skip-existing` 参数 | v8.4 |
| CASE_INFO 字典加 8 个新案例归档 | v8.4 |
| `06_searxng_crawl.py` 加 `--expand / --enrich` 标志 | v8.4 |

## ⚠️ 仍真失败 (诚实记录)

| 任务 | 真实状态 |
|---|---|
| A3 (4 奖项反爬修) | **0/4** — ADC 抓到 `adcawards.org/` 首页非 winners;Clio SPA fallback 全失败;OneShow SEED SPA 0 行 |
| B2 (06_searxng_crawl + enrich) | **理论 20 URL 找到,但 03 不写文件** — 直接调用 03 subprocess 只输出 stdout,无 raw.json 持久化 |
| 多层 fallback | **技术上生效但 URL 问题不是 fallback** — 4 奖项官方 winners URL 必须人工给 |

## 📊 真状态 (v8.4)

| 维度 | v8.3 | v8.4 |
|---|---|---|
| 真清单 | 85 | 85 (A3 没新增) |
| **真案例 (3 文件齐全)** | **9** | **17** ⬆️ +8 |
| 后台进程 | 0 | 0 (C2 已清) |
| 04_TOOLCHAIN | 8 | 8 (+case_runner_v2 arg) |

## 🔍 失败模式总结

| 期望修 | 实际修 |
|---|---|
| ADC 反爬 | ✅ SSL fallback,但 URL 是首页非列表 |
| Clio SPA | ❌ 多层 fallback 都失败 |
| OneShow SPA | ❌ SEED 命中但 0 行 |
| LongXi DNS | ❌ Wayback 2007 太旧,实际跳过 |
| Webby SPA | ❌ 未跑 |

## 🚀 v8.5 候选 (诚实)

| 选项 | 价值 |
|---|---|
| C3: 跑 v4 二次 (更深) | 新案例已 17,再跑可能增加 |
| B 任务用 case_runner_v2 真路径 | 取代 06_searxng 直接 enrich |
| v8.5 修 4 奖项 URL 给人工清单 | 必给真 URL,否则 0/4 |
| v8.5 写 STATUS 到 README 主索引 | 兼顾导览 |
