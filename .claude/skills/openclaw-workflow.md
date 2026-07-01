---
name: openclaw-workflow
description: 广告案例抓取 (via54_AD_AdCases_KB) 必须走 openclaw + WSL 工作流。本 SKILL 说明完整通路 + 工具链。
---

# openclaw-workflow SKILL (案例抓取专用)

## 为什么需要这个

`G:\agent\knowledge\reports\via54_AD_AdCases_KB\` 广告案例知识库的所有抓取任务
(SearXNG 搜索 / Chrome 渲染 / PDF 解析 / domain 校验) 必须强制走 **WSL + openclaw**
而不是 Windows 本地。原因:

1. **反爬严的 SPA** (canneslions.com / dandad.org / liaawards.com) 必须 Chrome 渲染
2. **WSL Chrome 149 + Playwright 1.60.0** 已装,直接用
3. **openclaw Gateway 18789 已在跑** (`{"ok":true,"status":"live"}`)
4. **openclaw 常驻 Chrome 18800** 已配 (`/home/via54/.openclaw/browser/openclaw/`)

## 核心工具 (已就绪)

| 工具 | 路径 | 说明 |
|---|---|---|
| **wsl_openclaw.py** | `04_TOOLCHAIN/wsl_openclaw.py` | 统一封装 `wsl -e bash -c "..."` + 4 种调用 |
| **03_collect_case.py** | `04_TOOLCHAIN/03_collect_case.py` | 单案例主入口 (已接入 wsl_openclaw) |
| **04_collect_award_winners.py** | `04_TOOLCHAIN/04_collect_award_winners.py` v3.2 | 清单抓取 + domain 校验 |
| **05_collect_all_cases.py** | `04_TOOLCHAIN/05_collect_all_cases.py` | 全量遍历清单 → 抽案例 → 调 03 |
| **enrich_case_cron.py** | `04_TOOLCHAIN/enrich_case_cron.py` | 30 案例/天 enrich (已接入 wsl_openclaw) |

## 调用模式 (Python)

```python
sys.path.insert(0, "G:/agent/knowledge/reports/via54_AD_AdCases_KB/04_TOOLCHAIN")
from wsl_openclaw import wsl_shell, wsl_python, wsl_chrome_fetch, wsl_pdftotext

# 1. 任意 shell
exit_code, stdout, stderr = wsl_shell("ls /mnt/g/agent/knowledge/")

# 2. WSL 跑 python 脚本 (自动 Windows→WSL 路径转)
exit_code, stdout, stderr = wsl_python(
    "G:/agent/.../03_collect_case.py",
    ["Three_Words", "Cannes_Grand_Prix"]
)

# 3. 反爬 SPA (走 WSL Chrome 渲染)
html = wsl_chrome_fetch("https://canneslions.com/...", timeout=90)

# 4. PDF 转文本
text = wsl_pdftotext("G:/agent/.../awards2025.pdf")
```

## 调用模式 (Bash / Cron)

```bash
# 单条 wsl
wsl -e bash -c "python3 /home/via54/agent/thdiff/scripts/clawlab-server.py"

# 路径直接用 Windows G: 盘 → WSL 自动 /mnt/g
wsl -e bash -c "cd /mnt/g/agent/knowledge/reports/via54_AD_AdCases_KB/04_TOOLCHAIN && python3 enrich_case_cron.py --max 30"
```

## Cron 任务 (enrich 30 案例/天)

- **Job ID**: `4bfe29bd9eed`
- **Schedule**: `0 5 * * *` (每天 06:05)
- **Delivery**: 原会话
- **状态**: ⚠️ **Gateway 离线时不会跑** — 手动触发用 `hermes cron run 4bfe29bd9eed`

## 真实依赖栈 (已就绪, 不必启)

| 服务 | 端口 | 状态 |
|---|---|---|
| **openclaw Gateway** | `http://localhost:18789` | ✅ UP `{"ok":true,"status":"live"}` |
| **openclaw Chrome** | `:18800` (remote-debugging) | ✅ UP |
| **WSL Chrome** | `/opt/google/chrome/chrome` | ✅ v149 |
| **Playwright (WSL)** | v1.60.0 | ✅ |
| **SearXNG** | `localhost:9086→8080` | ✅ UP (容器 `searxng_g`) |
| **Neo4j** | `bolt://localhost:7687` | ✅ UP (容器 `neo4j_g`) |
| **MinIO** | `127.0.0.1:9000-9001` | ✅ UP (容器 `minio_g`) |
| **Elasticsearch** (替代 Qdrant) | `localhost:9200` | ✅ UP (容器 `elasticsearch_g` green) |
| **Hermes Gateway** | `localhost:18792` | ✅ UP (`hermes gateway start`) |

## Pitfalls

- ⚠️ **WSL nohup 坑**: WSL bash 退出后,后台子进程会被 kill。**长跑 server 必须用 systemd / tmux / cron**,不是简单 `&`
- ⚠️ **端口冲突**: openclaw Chrome 占 18800,如果要改/用 orchestrator 改 `ORCHESTRATOR_PORT` 环境变量
- ⚠️ **WSL 路径**: Windows `G:\agent\...` → WSL `/mnt/g/agent/...`(`wsl_openclaw.py` 有 `win_to_wsl` helper)
- ⚠️ **`fetch_via_wsl_chrome` vs `wsl_chrome_fetch`**: 前者写死 18800,后者每次新启 — **用 wsl_chrome_fetch** (统一封装)
- ⚠️ **Gateway 不在 18789 之外**: openclaw 占 18789,hermes gateway 在 18792,**不冲突**但别混用

## 常见任务执行模板

### A. 抓单个新案例
```bash
python 03_collect_case.py "Case Name" "Cannes_Grand_Prix" --source-url https://...
```
(内部自动先 requests,失败走 wsl Chrome)

### B. 全量抓所有清单前 2 案例
```bash
python 05_collect_all_cases.py --per-file 2 --sleep-between 0.5
```

### C. cron enrich 30 案例/天 (后台,跳过已完成)
```bash
python enrich_case_cron.py --max 30 --skip-existing
```

### D. 抓新清单
```bash
python 04_collect_award_winners.py --year 2025 --award Effie_Awards/North_America --category Gold
```

## 参考文档

- 项目 STATUS: `G:\agent\knowledge\reports\v...03_collect_case.py`
- 工具链 README: `G:\agent\knowledge\reports\via54_AD_AdCases_KB\04_TOOLCHAIN\README.md`
- v6.0 状态: `via54ADIdeahub/docs/STATUS.md`
