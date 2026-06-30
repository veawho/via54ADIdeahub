# via54_AD_AdCases_KB 项目状态 — v4.0 (误标修正后)

> 最后更新: 2026-07-01 06:38
> 工具版本: 04_collect_award_winners.py v3.2 (PDF + SEED_URLS + domain 校验)
> KB 状态: **0 占位 / 81 真文件 / 真数据从权威源**

## 一、知识库总览

```
via54_AD_AdCases_KB/
├── 00_RULES/RULES.md v3.0 (md5 a29d27afc67c1d5d3e994133f0096aae)
├── 01_STACK/
├── 02_AWARD_SOURCES/ ★ 81 真清单 (domain 校验后)
├── 03_TEMPLATES/
├── 04_TOOLCHAIN/ ★ 6 脚本 + 8 batch yaml
├── 05_CASES/By_Industry/ ★ 6 真实案例 (AXA/Dove/Natura/Coca-Cola/Specsavers/Channel 4)
├── 99_LOGS/STATUS.md (本文件)
└── README.md
```

## 二、数据覆盖 — 真实数据 (v4.0 domain 校验后)

| 奖项 | 真文件 | 数据源 (domain) | 状态 |
|---|---|---|---|
| **Cannes_Lions** | 39 | canneslions.com / lionswork.com | ✅ 真 |
| **Effie_Awards** | 20 | effie.org / apaceffie.com / s3.amazonaws | ✅ 真 |
| **DAD** | 10 | media.dandad.org (PDF) | ✅ 真 |
| **LIA** | 7 | liaawards.com | ✅ 真 |
| **Spikes_Asia** | 5 | spikes.asia | ✅ 真 |
| ADC_Annual | 0 | (SearXNG 失败) | ⚠️ 0 |
| Clio | 0 | (SearXNG 失败 - clios.com SPA) | ⚠️ 0 |
| One_Show | 0 | (SearXNG 失败) | ⚠️ 0 |
| Webby | 0 | (SearXNG 失败) | ⚠️ 0 |
| Long_Xi | 0 | (中文源稀缺) | ⚠️ 0 |
| **TOTAL** | **81** | **5 奖项真数据 + 5 奖项待补** | |

## 三、真实案例归档 (06 真案例 in 05_CASES/By_Industry/)

| # | 案例名 | 品牌 | 行业 | 主奖项 |
|---|---|---|---|---|
| 1 | Three Words | AXA | Insurance | Cannes Dan Wieden Titanium GP |
| 2 | Real Beauty Sketches | Dove | Beauty | Cannes Cyber Lion GP |
| 3 | Amazon Greenventory | Natura | Beauty | Cannes Creative B2B GP |
| 4 | Recycle Me | Coca-Cola | Food/Bev | Cannes Sustainable Dev GP |
| 5 | Misheard Version | Specsavers | Retail | Cannes Audio/Radio GP |
| 6 | Paris 2024 Paralympics | Channel 4 | Sports | Cannes Entertainment GP |

## 四、v4.0 关键修正 (误标防护)

**问题**:subagent `deleg_4ad53570` 时代,SearXNG 返回汇总页 (llllitl.fr / creativereview.co.uk / adweek.com),工具无 domain 校验,误标到子奖项目录。

**修正**:
1. 删 34 个误标文件 + 1 个 ADC = **35 个错位文件删除**
2. 工具加 `_validate_source_domain` 函数 + `domain_mismatch` 状态
3. domain 白名单 (10 奖项 × 各自合法 domain)
4. s3.amazonaws.com 镜像单独放行 (Effie PDF)

## 五、工具栈 v3.2

| 工具 | 状态 | 备注 |
|---|---|---|
| SearXNG (searxng_g) | ✅ | 默认引擎: bing/yahoo/reddit |
| WSL Chrome 149 | ✅ | /opt/google/chrome/chrome |
| Playwright 1.60.0 | ✅ | |
| 04_collect_award_winners.py | ✅ v3.2 | PDF + SEED_URLS + domain 校验 |
| 03_collect_case.py | ✅ | 单案例 enrich |
| case_runner_v2.py | ✅ | 批量抽案例 |

## 六、git 提交历史

- `108977b` feat(toolchain): domain 校验防误标
- `2d33237` feat(toolchain): 04_collect_award_winners.py v3.1 — PDF 解析 + SEED_URLS

## 七、cron 阶段 6 已启动

- **Cron job `4bfe29bd9eed`**: 每 24h 自动跑 enrich_case_cron.py --max 30

## 八、已知问题

1. **5 奖项 0 真数据** — ADC/Clio/One_Show/Webby/LongXi (SearXNG 失败, 需要专门搜索策略)
2. **Effie 部分含噪声** — PDF 块结构启发式需更精准模板
3. **3 案例 (Apple/Dramamine/Siemens) 反爬严**,抓 0 数据
4. **LongXi 中文奖项** — SearXNG 中文引擎弱,待专门搜索
