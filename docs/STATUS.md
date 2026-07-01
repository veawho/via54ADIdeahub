# via54_AD_AdCases_KB 项目状态 — v8.1 (B 任务结果审计)

> 最后更新: 2026-07-01 17:30
> 作者: via54 + Hermes Agent
> 状态: **B 任务审计后真实**

## ⚠️ v8.0 → v8.1 修正 (真相汇报)

### B 任务 (05_collect_all_cases 全量抓 81 清单前 2 案例) — **0/138 成功**

跑完结果:
```
[138/138] Joe Ando  → WARN no JSON (Webby 是真人创作者,不是广告)
=== 完成: 0/138 成功 ===
```

**根因**:
- 81 清单里很多含"Glass: The Lion for Change"/"Film Lions"/"PR - MarketingDirecto"/"Special US • PHD" 等噪声
- 工具抽到的前 2 行通常是子奖项名/新闻标题,搜不出真案例
- 真实可达: **9 真案例** (enrich 完成 = 真案例完整)

### 清理动作

✅ 清 Unknown/ 下 24 个 0 字节噪声空目录 (Glass/Film Lions/Audio/Brand/04/04/...)
✅ 清 22 个空目录
✅ Unknown/ 残留 0

## 🎯 v8.0 真实数字 (审计后)

| 维度 | 数字 | 备注 |
|---|---|---|
| **02_AWARD_SOURCES 真清单** | **82** | v7.0 81 + Webby 2025 Winner (1) |
| **05_CASES 真案例** | **9** | 全部 5 文件齐全(raw.json + FOLDER_README + 概述 + 深度报告 + 视频清单)|
| **B 任务全量尝试** | **138 案例抓取尝试** | 0 成功 (清单噪声太多,见上) |
| **Task A (5 奖项) 结果** | **1/10 成功** | Webby 2025 Only |
| **adcase_api server** | ✅ UP `http://localhost:18900` | PID 24580 |
| **Cron 状态** | ⚠️ Gateway not running, 手动 OK | 已知限制 |

## 🧠 学到的关键

1. **清单噪声严重**: 81 清单里 >50% 抓的是 PR/新闻/描述,不是"案例名列表"
2. **B 任务不会从坏清单里找出真案例**: 修好工具不够,**修源**(04_collect_award_winners.py 抓的清单)才是
3. **STATUS 数字失实历史**: v3.0-v8.0 我 4 次报过虚高 (117/1296/4/9 case 数字反复), 真实 = 9 真案例 + 82 真清单

## 🟢 9 真案例 (审计后)

1. **Three Words** (AXA / Insurance) - 5 文件齐全
2. **The Misheard Version** (Specsavers / Retail) - 5 文件齐全
3. **Recycle Me** (Coca-Cola / Food_Beverage) - 5 文件齐全
4. **Real Beauty...Self-Esteem Movement** (Dove / Beauty_Personal_Care) - 5 文件齐全
5. **The Amazon Greenventory** (Natura / Beauty_Personal_Care) - 5 文件齐全
6. **The Last Barf Bag** (Dramamine / Pharmaceutical) - 5 文件齐全
7. **Magnetic Stories** (Siemens Healthineers / Healthcare_MedTech) - 5 文件齐全
8. **Shot on iPhone** (Apple / Technology) - 5 文件齐全
9. **Paris Paralympics 2024 Considering What** (Channel 4 / Media_Entertainment) - 5 文件齐全

## 🚀 工具栈 (8 件, v8.0 落地)

| 文件 | 作用 |
|---|---|
| `wsl_openclaw.py` | 统一 `wsl -e bash -c "..."` 封装 |
| `04_collect_award_winners.py` v3.2 | 清单抓 |
| `03_collect_case.py` | 单案例 (含 WSL Chrome fallback) |
| `enrich_case_cron.py` | 30 案例/天 enrich |
| `05_collect_all_cases.py` | 全量遍历 (B 任务用) |
| **`adcase_api.py`** | **HTTP 入口 18900 (语义分派后端)** |
| `task_A_5awards.yaml` | 5 奖项批次配置 |
| `openclaw-intent-dispatch.md` SKILL | 4 类意图分派规则 |

## 🔴 待修 / 未完成

1. **清单噪声**: 需修 `04_collect_award_winners.py` 清单解析 — 只接受"`for X by Y`"结构
2. **Task A 9 FAIL**: ADC/Clio/OneShow/LongXi 反爬严或 DNS 不通 — 需 wayback fallback
3. **Webby 2024**: SPA 解析 0 行 — 走 WSL Chrome 即可修
4. **openclaw ↔ adcase_api 整合**: 写 telegram bot 调 `POST /collect` (后置项)
5. **Gateway 起 cron 24h**: 用户说"启 Gateway"才动
