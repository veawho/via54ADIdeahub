---
name: openclaw-intent-dispatch
description: windows-hermes 主对话的"语义分派"规则 — 根据用户意图自动走 wsl-openclaw 工作流,而不是按命令名固定路由
---

# openclaw-intent-dispatch SKILL (语义分派)

## 🎯 核心原则

**不是 "关键词匹配 → 命令"**,而是 **"意图识别 → 工具选择"**。
windows-hermes (主对话) 收到用户消息时,**先识别意图分类**,
再选最合适的 wsl-openclaw 工具组合。

## 🚦 4 类语义意图

### A. 案例抓取 / 内容获取 (crawl)

**触发信号** (语义,非关键词):
- "抓 [X] 案例 / 案例详情 / 案例数据"
- "找 [X] 广告 / 广告案例 / 获奖案例"
- "[X] 这个奖的得主 / 名单 / winners"
- "怎么抓 / 怎么找 / 怎么爬"

**分派 →** `wsl_openclaw.wsl_chrome_fetch` 或 `03_collect_case.py`
**接口 →** `POST /collect` (`adcase_api.py:18900`)
**搜索路径:** SearXNG 先 → URL → WSL Chrome 渲染

### B. 案例 enrich / 深度报告 (enrich)

**触发信号**:
- "深化 / enrich / 深度报告 / 概述.md / 视频清单"
- "补全 / 补全案例"
- "cron 跑一下"

**分派 →** `enrich_case_cron.py`
**接口 →** `POST /enrich` (`adcase_api.py:18900`)
**依赖:** API server 必须跑 (`python adcase_api.py`)

### C. 全面批次 / 批量 (crawl_all)

**触发信号**:
- "全部 / 所有 / 全量 / 后台跑 / 162"
- "抓所有清单 / 每个清单 N 案例"

**分派 →** `05_collect_all_cases.py`
**接口 →** `POST /crawl/all` (`adcase_api.py:18900`)

### D. 列表查询 / 元数据 (list)

**触发信号**:
- "现在有什么 / 现状 / 进度 / 清单在哪 / 抓到了什么"

**分派 →** `GET /list/awards` 或 `GET /list/cases` (`adcase_api.py:18900`)

## 🔍 语义识别 (在主对话每个回合判断)

收到用户消息时:
1. **解析意图** (A/B/C/D)
2. **提取实体** (案例名 / 奖项 / 品牌 / URL)
3. **调 adcase_api.py:18900** 对应端点
4. **WARN if domain mismatch** — 这是来自 KB 内部的关键校验

## 🛑 反例: 不要按命令匹配

❌ **错误** (固定规则): "用户说 `python xxx.py` → 跑 `python xxx.py`"
✅ **正确** (语义): "用户说 `抓 [Y] 案例` (语义) → 不管命令是不是 python → 调 `POST /collect`"

## 🧪 测试用例

| 用户原话 | 语义识别 | 分派 |
|---|---|---|
| "AXA Three Words 案例" | A crawl | POST /collect {"case_name":"AXA Three Words"} |
| "后台 enrich 30 个" | B enrich | POST /enrich {"max_cases":30} |
| "全量抓 81 清单" | C crawl_all | POST /crawl/all {"per_file":2} |
| "现在状态怎样" | D list | GET /list/awards |
| "把所有 [空数据] 奖项重抓" | A crawl (mixed) | POST /collect (循环) + crawl_all |

## 🔗 相关资源

- **adcase-api**: `G:/agent/knowledge/reports/via54_AD_AdCases_KB/04_TOOLCHAIN/adcase_api.py` (port 18900)
- **wsl-openclaw**: `04_TOOLCHAIN/wsl_openclaw.py`
- **openclaw-workflow**: `.claude/skills/openclaw-workflow.md` (案例抓取)
- **本 SKILL**: `.claude/skills/openclaw-intent-dispatch.md` (语义分派)

## Pitfalls

- ⚠️ **A 与 C 的边界**: 单个明确案例 = A, 全量/批量 = C (per_file N)
- ⚠️ **B enrich 跳过已完成**: --skip-existing 默认 True (`/enrich` 已含)
- ⚠️ **POST /crawl/all**: 长任务 (默认 4h timeout),**应用背景异步触发**
- ⚠️ **GET /list/awards**: 返回 `_cases.total` 是按 rglob `*Cannes_Grand_Prix` 统计,**仅代表某种类型**,真实案例数应看 99_LOGS/STATUS.md
