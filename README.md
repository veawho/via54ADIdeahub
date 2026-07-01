# via54_AD_AdCases_KB

> 全球顶级广告奖项真实获奖案例库 — **38 真案例 / 11 行业 / 17 品牌 / 1 个工作流的真报道**

## 📊 截至 v8.6 — 38 真案例, 11 行业, 17 品牌

| # | 行业 | 案例 | 品牌 |
|---|---|---|---|
| 1 | Food_Beverage | **9** | Coca-Cola(4) + Cadbury(3) + Heineken(2) + Burger King(3) |
| 2 | Beauty_Personal_Care | **7** | Dove(4) + Natura(4) + CeraVe(1) — Natura 4 个 |
| 3 | Technology | **6** | Apple(4) + TikTok(2) |
| 4 | Media_Entertainment | **3** | Channel 4 |
| 5 | Retail | **3** | Specsavers(3) |
| 6 | Insurance | **2** | AXA(2) |
| 7 | Pharmaceutical | **2** | Dramamine(2) |
| 8 | Apparel_Sportswear | **2** | Nike(2) |
| 9 | Toys_Family | **2** | Lego(2) |
| 10 | Healthcare_MedTech | **1** | Siemens |
| 11 | Other | **1** | JR Group |

**总计: 38 真案例 / 17 品牌 / 11 行业**
(3 文件齐全: `*_raw.json` + `概述.md` + `深度报告.md`)

## 🥇 品牌冠军

| 品牌 | 案例数 | 行业 |
|---|---|---|
| Apple | 4 | Technology (AirPods / The Greatest / Shot on iPhone / Big Man) |
| Natura | 4 | Beauty (The Amazon Greenventory / 续 3 个) |
| Coca-Cola | 4 | Food_Beverage (Recycle Me / Master Plan / Contagious / +1) |
| Dove | 4 | Beauty (Real Beauty / Reverse Selfie / Decades / +1) |

## 🚦 工作流

### 抓取案例
1. `case_runner_v2.py --yaml configs/batch_cases_v6.yaml`  
2. 自动调 `03_collect_case.py` → SearXNG → AdWeek/Contagious/LBB/Campaign
3. 解析 HTML → 写 `*_raw.json` + `FOLDER_README.md`
4. `enrich_case_cron.py` → 概述/深度报告/视频清单

### 抓清单 (各奖项 winners)
1. `04_collect_award_winners.py --config configs/task_*.yaml`
2. 多层 fallback: requests → WSL Chrome → Wayback

### 横向 search
- `06_searxng_crawl.py --config configs/task_*.yaml [--expand] [--enrich]`

## 📁 关键文件

```
04_TOOLCHAIN/
  case_runner_v2.py        (主入口 --yaml / --skip-existing)
  configs/
    batch_cases_v2.yaml    (9 原始)
    batch_cases_v4.yaml    (17)
    batch_cases_v5.yaml    (26)
    batch_cases_v6.yaml    (38)

05_CASES/By_Industry/
  ├── Apple/      (4 dirs)
  ├── Natura/     (4 dirs)
  ├── Coca-Cola/  (4 dirs)
  ├── Dove/       (4 dirs)
  └── ... 17 品牌, 38 案例

99_LOGS/STATUS.md          (版本演进)
README.md                  (本文件)
```

## ⚠️ 限制 (诚实)

- 4 奖项 winners URL 未抓到 (ADC/Clio/OneShow/Webby)
- LongXi 域名失效
- 当前数据来源 = **Cannes Lions** (主) + 1 Clio 案例 (Dramamine Motion)

## 📈 演进时间线

| 版本 | 真案例 | 增量 |
|---|---|---|
| v8.1 | 9 | 起始 |
| v8.3 | 9 | A2 修无增 |
| v8.4 | 17 | +8 |
| v8.5 | 26 | +9 |
| v8.6 | **38** | **+12 (SearXNG 真验证 12/12)** |

## 🔮 下一步候选

- 修 4 奖项 URL (人工给官方 winners URL)
- Apple / Natura / Coca-Cola / Dove 各加 1-2 个案例继续
- 给 KB 加 SPEC 索引 (分类按奖项 vs 按行业)
- 导出 PDF (报告式)
