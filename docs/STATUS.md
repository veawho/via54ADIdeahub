# via54_AD_AdCases_KB 项目状态 — v7.0 (wsl-openclaw 工作流)

> 最后更新: 2026-07-01
> 作者: via54 + Hermes Agent
> 状态: **wsl-openclaw 通路已通**

## 🎯 v6.0 → v7.0 核心变化

### ✅ 关键交付物 (今天新增)

| 交付物 | 路径 | 用途 |
|---|---|---|
| **`wsl_openclaw.py`** | `04_TOOLCHAIN/wsl_openclaw.py` (4.9KB) | **统一封装 `wsl -e bash -c "..."`** + 4 调用 (shell/python/chrome/pdf) |
| **`03_collect_case.py`** 改造 | `fetch_page()` 失败自动走 `wsl_chrome_fetch` | 反爬严 SPA 自动 fallback |
| **`enrich_case_cron.py`** 改造 | 引入 `from wsl_openclaw import wsl_python` | cron 自动走 WSL |
| **`openclaw-workflow.md`** SKILL | `via54ADIdeahub/.claude/skills/` | 案例抓取工作流规范 |

### ✅ 真实依赖栈 (调研后真相)

| 服务 | 端口 | 状态 | 备注 |
|---|---|---|---|
| **openclaw Gateway** | `localhost:18789` | ✅ UP | **Node.js** v2026.6.10,`{"ok":true,"status":"live"}` |
| **openclaw Chrome** | `:18800` remote-debugging | ✅ UP | `/home/via54/.openclaw/browser/openclaw/` |
| **Hermes Gateway** | `localhost:18792` | ✅ UP | `hermes gateway start` 起的 |
| **WSL Chrome** | `/opt/google/chrome/chrome` | ✅ v149 | Playwright 1.60.0 |
| **SearXNG** | `localhost:9086→8080` | ✅ UP | 容器 `searxng_g` |
| **Neo4j** | `bolt://localhost:7687` | ✅ UP | 容器 `neo4j_g` |
| **MinIO** | `127.0.0.1:9000-9001` | ✅ UP | 容器 `minio_g` |
| **Elasticsearch** | `localhost:9200` | ✅ green | 容器 `elasticsearch_g`,**替代 Qdrant** |
| **8 thdiff agents** | 18801-18808 (FastAPI) | ⚠️ UP | thdiff clawlab/knowledgelab/...,非案例抓取路径 |

### 🔴 调研误判(诚实记录)

1. **`wsl-openclaw` ≠ thdiff `clawlab agent`**: 我一度混淆,**真实 openclaw 是 Node.js AI Gateway** (npm 包)
2. **Qdrant 配置在 yaml 但实际用 Elasticsearch**: KB 配置 `collection: hermes-knowledge (Qdrant)`,栈里只装了 Elasticsearch,**不矛盾但要用 ES**
3. **thdiff clawlab (政策金融情报)** ≠ 广告案例抓取 agent: thdiff 项目有自己的 agent 体系

## 🎯 现状数字 (3 次 audit 后)

- **02_AWARD_SOURCES 真清单: 81**
- **05_CASES/By_Industry 真案例: 9** (Dove/Natura/Coca-Cola/Siemens/AXA/Channel 4/Dramamine/Specsavers/Apple)
- **抓取工具链: 5** (`04_collect_award_winners.py` v3.2 + `03_collect_case.py` + `enrich_case_cron.py` + `05_collect_all_cases.py` + `wsl_openclaw.py`)

## 🚀 未来任务 (Post v7.0)

- [ ] 重抓 Effie 2024 / D&AD / LIA (清单是新闻/导航页,需找真源)
- [ ] 抓 ADC / Clio / One_Show / Webby / LongXi (5 奖项 0 真数据)
- [ ] 把 9 真案例深度报告中的 Qdrant 引用换成 Elasticsearch
- [ ] `05_collect_all_cases.py` 过滤放宽后重跑 162 案例
- [ ] 给 openclaw Gateway 配 ad-case-study-kb 适配器
