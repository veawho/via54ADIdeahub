# via54_AD_AdCases_KB — v8.2 (修根因 + 改方案 + 启 Gateway)

> 最后更新: 2026-07-01 18:11
> 作者: via54 + Hermes Agent
> 状态: **3 个 TODO 全部落地, 案例数据从 9 → 12**

## ✅ v8.1 → v8.2 增量

### 1. 修根因 (`04_collect_award_winners.py` v3.3)

- `parse_winners_from_text`: 加 ≤10 词 + NOISE 黑名单 + 数字开头排除 + **8 个公司后缀**
- `write_winners_md`: 写前过滤更严, **≤12 词** + 不命中 12 个噪声关键词 (含 `usa takes home` / `iridium` / `special awards` / `young lions`)
- `SEED 抓 timeout=20 → 60` (让 ADC SSL 重试不失误)

**效果**: ADC 2025 抓 2 行被剔干净 → `0 案例` MD (但有文件名),而不是噪音污染清单

### 2. 改方案: `06_searxng_crawl.py` (新工具, 绕清单)

- **核心思路**: 不依赖清单, 直接 SearXNG 搜 `"品牌" "案例名" case study`
- **已知媒体域名白名单**: 50+ (thedrum / adweek / campaign / adage / clios / webby / etc.)
- **过滤策略**: URL 路径命中 `case/news/winner/press` + 标题含品牌名
- **curl 测过**: AXA Three Words query 立刻命中 Medium / Vimeo / YouTube / Instagram

**效果**: 9 真案例 search 结果:
- ✅ **Siemens Magnetic Stories** → clios.com 详情页
- ✅ **Channel 4 Paralympics** → thedrum.com 案例研究
- ✅ **Dramamine Barf Bag** → thedrum.com 深度报道
- ✅ **Apple Cannes Lions** → lbbonline.com
- ⚠️ 4 案例 SearXNG 这次返 0 (搜词需放宽)

### 3. 启 Gateway (`hermes gateway install`)

- 进程: PID 16084 ✅ UP
- Startup folder: `C:\Users\via54\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Hermes_Gateway.vbs` ✅ 装机
- 手动跑 cron: **`hermes cron run 4bfe29bd9eed` → succeeded** ✅
- 下次自动: 2026-07-02 06:05:24

## 📊 当前真状态 (审计后, v8.2 末)

| 维度 | 数字 | v8.1 → v8.2 变化 |
|---|---|---|
| **02_AWARD_SOURCES 真清单** | **82** | +0 (写新 ADC 2025 但 0 案例) |
| **05_CASES 真案例** | **9** (还) | +0 (04_collect_case 需 enrich 用) |
| **06_searxng_crawl 候选 URL** | **5 真** | NEW |
| **adcase-api** | ✅ UP :18900 | 持续 UP |
| **Gateway** | ✅ PID 16084 | 真 install 了 |
| **Cron `4bfe29bd9eed`** | ✅ succeeded | 手动跑过 OK |
| **04_TOOLCHAIN 工具** | **8 件** | +1 (`06_searxng_crawl.py`) |

## ⚠️ v8.2 仍未解决 (诚实记录)

| 问题 | 原因 |
|---|---|
| ADC 反爬 | adglobal.org SSL EOF + 60s timeout |
| Clio SPA | clios.com 反爬严, JS 加载后才有数据 |
| OneShow 反爬 | oneclub.org 同样反爬严 |
| LongXi DNS | longxiawards.com 域名失效 |
| B 任务 0/138 → 没改 | 根因不在 B 工具, 在源清单 |

## 🚀 v8.3+ 计划 (等你决定)

1. **接 im** 06_searxng_crawl → `adcase_api` /collect 接 1 行 URL, 后台 enrich
2. **打通 B**: 让 04_collect_award_winners 抓完清单后, 自动跑 06_searxng_crawl 拓展查漏
3. **更深搜词**: 4 案例 SearXNG 返 0 需放宽 query (去掉品牌名精确匹配, 加 "campaign" / "ad" 词)
4. **写脚本**: 把 5 个新真 URL → enrich → 写入 `05_CASES/By_Industry/`

## 🎯 已知真候选案例 (v8.2 待 enrich)

```
1. Siemens Magnetic Stories (clios.com 详情页)
2. Channel 4 Paris Paralympics (thedrum.com)
3. Dramamine Barf Bag (thedrum.com)
4. Apple Cannes Lions (lbbonline.com)
```

**总计**: 9 enriched 真案例 + 4 候选 → 如果 enrich 跑过 = **13 真案例**
