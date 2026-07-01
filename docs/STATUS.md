# via54_AD_AdCases_KB 项目状态 — v8.0 (5 奖项 + 语义分派)

> 最后更新: 2026-07-01 17:01
> 作者: via54 + Hermes Agent
> 状态: **wsl-openclaw 工作流 + 语义分派已通**

## 🎯 v7.0 → v8.0 增量

### ✅ 新增交付物

| 文件 | 路径 | 用途 |
|---|---|---|
| **`adcase_api.py`** | `04_TOOLCHAIN/adcase_api.py` (3.7KB) | **本地 HTTP API server** port 18900 |
| **API 端点** | 5 个: `/health` / `/collect` / `/list/awards` / `/list/cases` / `/enrich` / `/crawl/all` | ad-case-study-kb 接入入口 |
| **`task_A_5awards.yaml`** | `04_TOOLCHAIN/configs/task_A_5awards.yaml` | 5 奖项批次配置 |
| **`openclaw-intent-dispatch.md`** SKILL | `via54ADIdeahub/.claude/skills/` | 语义分派规则 (4 类意图 A/B/C/D) |
| **Task A 结果** | `02_AWARD_SOURCES/WebbyAwards/...` | **1/10 成功 — Webby 2025 3 案例** |

### ✅ 工具栈全景 (v8.0)

| 工具 | 作用 |
|---|---|
| `wsl_openclaw.py` | 统一 `wsl -e bash -c "..."` 封装 (4 调用) |
| `04_collect_award_winners.py` v3.2 | 清单抓取 (SearXNG → SEED → WSL Chrome) |
| `03_collect_case.py` | 单案例抓取 (requests → WSL Chrome fallback) |
| `enrich_case_cron.py` | 30 案例/天 enrich (走 wsl_openclaw) |
| `05_collect_all_cases.py` | 全量遍历清单 → 抽案例 → 调 03 |
| **`adcase_api.py`** (新) | **HTTP server 18900 入口** (POST /collect /enrich /crawl/all) |
| **`openclaw-intent-dispatch.md`** (新) | 语义分派规则 (按意图路由,不是按命令) |

### ✅ 语义分派 (D 任务)

windows-hermes 主对话按"意图"分派到 wsl-openclaw:
- **A intent (crawl)** → `POST /collect`
- **B intent (enrich)** → `POST /enrich`
- **C intent (crawl_all)** → `POST /crawl/all`
- **D intent (list)** → `GET /list/awards` 或 `/list/cases`

## 📊 当前真数据

| 维度 | 数字 | 备注 |
|---|---|---|
| **02_AWARD_SOURCES 真清单** | **82** (v7.0 的 81 + Webby 2025 Winner) | 任务 A 加 1 |
| **05_CASES 真案例** | **9** (3 Words/Recycle Me/Real Beauty/Amazon Greenventory/Magnetic Stories/Paris Paralympics/Last Barf Bag/Misheard Version/Shot on iPhone) | 没增长(B 后台跑) |
| **API server** | ✅ UP `http://localhost:18900` | PID 24580 |
| **Cron 状态** | ⚠️ Gateway is not running — 手动触发 OK | (已知问题,等用户决定启 Gateway) |

## 🔴 Task A 详细结果 (1/10)

| 奖项 | 年份 | 结果 | 备注 |
|---|---|---|---|
| ADC | 2024 | ❌ FAIL | adglobal.org read timeout (20s 太短) |
| ADC | 2025 | ❌ FAIL | 同上 |
| ClioAwards | 2024 | ❌ FAIL | SearXNG+SEED 没找 |
| ClioAwards | 2025 | ❌ FAIL | clios.com SPA 反爬严 |
| OneShow | 2024 | ❌ FAIL | oneclub.org 反爬 |
| OneShow | 2025 | ❌ FAIL | 同上 |
| WebbyAwards | 2024 | ❌ FAIL | winners.webbyawards.com SPA 解析 0 行 |
| **WebbyAwards** | **2025** | ✅ **1 成功** | www.webbyawards.com 命中,3 案例(是真人创作者非广告) |
| LongXi_Awards | 2024 | ❌ FAIL | longxiawards.com DNS 不通 |
| LongXi_Awards | 2025 | ❌ FAIL | 同上 |

**结论**: 大多数**反爬严/域名失效**。需要:
1. 把 SEED 抓 timeout=20 改成 60+
2. 加更多 fallback URL (wayback.archive.org 等)
3. 或直接抓这些站的 sitemap

## 🧠 学到的真实架构

1. **openclaw (Node.js v2026.6.10) ≠ thdiff clawlab agent**
   - openclaw = IM gateway (Telegram/Slack → AI)
   - thdiff agents = research agent (政策金融/知识/审计)
2. **真正的"广告案例 wsl-openclaw 工作流" = 自己写的 Python 工具栈**
   - `wsl_openclaw.py` + `adcase_api.py` + `04_TOOLCHAIN/`
3. **windows-hermes 主对话 应"按语义分派"而不是"按命令匹配"**
   - 用户说"抓 [X]" (语义) → 不管命令怎么写 → `POST /collect`

## 🚀 后续建议 (等用户决定)

- ⏸️ **修复 Task A 失败**: 改 SEED timeout=60+; 加 wayback fallback
- ⏸️ **修复 Webby 2024 SPA**: 走 WSL Chrome 渲染即可
- ⏸️ **B 后台跑中** (proc_932ab3d973f6): 进度待观察
- ⏸️ **整合 openclaw → adcase_api**: 写 telegram/discord IM bot 调 `POST /collect`
