# via54_AD_AdCases_KB 项目状态 — v5.0 (最终真实状态)

> 最后更新: 2026-07-01 06:40
> 工具版本: 04_collect_award_winners.py v3.2 (PDF + SEED_URLS + domain 校验)
> KB 状态: **0 占位 / 81 真清单 / 4 真案例归档**

## 一、知识库总览 (真实状态)

```
via54_AD_AdCases_KB/
├── 00_RULES/RULES.md v3.0
├── 02_AWARD_SOURCES/ ★ 81 真清单 (domain 校验后)
├── 04_TOOLCHAIN/ ★ 6 脚本 + 8 batch yaml
├── 05_CASES/By_Industry/ ★ 4 真实案例 (清理错位后)
└── 99_LOGS/STATUS.md
```

## 二、02_AWARD_SOURCES 真数据 (v5.0)

| 奖项 | 真文件 | 数据源 (domain) | 状态 |
|---|---|---|---|
| **Cannes_Lions** | 39 | canneslions.com | ✅ |
| **Effie_Awards** | 20 | effie.org / apaceffie.com / s3.amazonaws | ✅ |
| **DAD** | 10 | media.dandad.org (PDF) | ✅ |
| **LIA** | 7 | liaawards.com | ✅ |
| **Spikes_Asia** | 5 | spikes.asia | ✅ |
| ADC_Annual | 0 | (SearXNG 失败) | ⚠️ 0 |
| Clio | 0 | (SearXNG SPA 反爬) | ⚠️ 0 |
| One_Show | 0 | (SearXNG 失败) | ⚠️ 0 |
| Webby | 0 | (SearXNG 失败) | ⚠️ 0 |
| Long_Xi | 0 | (中文源稀缺) | ⚠️ 0 |
| **TOTAL** | **81** | **5 奖项真数据 + 5 奖项待补** | |

## 三、05_CASES/By_Industry 真案例归档 (4 个)

| # | 案例 | 品牌 | 行业 | 主奖项 | 文件 |
|---|---|---|---|---|---|
| 1 | Three Words | AXA | Insurance | Cannes Dan Wieden Titanium GP | raw.json + FOLDER_README |
| 2 | The Amazon Greenventory | Natura | Beauty_Personal_Care | Cannes Creative B2B GP | raw.json + FOLDER_README |
| 3 | Recycle Me | Coca-Cola | Food_Beverage | Cannes Sustainable Dev GP | raw.json + FOLDER_README |
| 4 | The Misheard Version | Specsavers | Retail | Cannes Audio/Radio GP | raw.json + FOLDER_README |

## 四、v5.0 关键修正

### v4.0 (数据源 domain 校验)
- 删 34 个误标 (subagent 时代汇总页归档)
- 加 _validate_source_domain 函数

### v5.0 (案例归档清理)
- 删 4 个错位归档 (Unknown/Three, Unknown/Shot, Unknown/Real, Unknown/Paris)
- 删 1 个旧版目录 (AXA/Three_Words_Cannes_Grand_Prix)
- 删 5 个空目录
- **真案例从 6 → 4** (Dove/Real Beauty 和 Channel 4/Paris Paralympics 实际无 raw.json)

## 五、已知问题 (诚实)

1. **5 奖项 0 真数据**: ADC/Clio/One_Show/Webby/LongXi
   - Clio SPA 反爬 (Wayback 已内置)
   - One_Show theoneclubforcery.com 待真源 URL
   - Webby webbyawards.com 待真源 URL
   - ADC/LongXi 长尾奖项需专门搜索策略
2. **5 个案例 raw.json 缺失/空**:
   - Apple Shot on iPhone (反爬严)
   - Dramamine The Last Barf Bag (反爬严)
   - Siemens Healthineers Magnetic Stories (反爬严)
   - Dove Real Beauty (从未归档)
   - Channel 4 Paris Paralympics (从未归档)
3. **Effie 部分含噪声** — PDF 块结构启发式需更精准模板
4. **案例名 sanitize 改进**: Real Beauty 应缩短为 "Real Beauty Sketches"

## 六、git 提交

- `108977b` feat(toolchain): domain 校验防误标
- `2d33237` feat(toolchain): 04_collect_award_winners.py v3.1 — PDF 解析
- `adb688e` docs: STATUS.md v4.0

## 七、cron 已启动

- **Cron `4bfe29bd9eed`**: 每 24h enrich 30 案例
- 首次跑: 2026-07-02 06:05
