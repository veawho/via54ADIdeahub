# via54 AD 案例知识库 (via54_AD_AdCases_KB) — 规则手册

> **本文件是知识库的最高规则,任何脚本/agent 抓取案例前必须读取本文件。**
> **适用项目**: `G:\agent\ai\projects\via54ADIdeahub` (via54ADIdeahub)
> **知识库根**: `G:\agent\knowledge\reports\via54_AD_AdCases_KB\`
> **创建日期**: 2026-07-01
> **版本**: v1.0

---

## 规则 1 — 案例来源分级 (Source Tiering)

### 优先 1 — 全球广告大奖官网 (官方权威源)

| 奖项 | 主域名 | 子奖项 (按地区/品类) |
|---|---|---|
| **Cannes Lions 戛纳国际创意节** | `canneslions.com` | Lions Health, Lions Entertainment, Lions Innovation, Lions Digital, Lions Print, Lions Film, Lions Audio, Lions Outdoor, Lions Direct, Lions Media, Lions Design, Lions Industry Craft |
| **Effie Awards 艾菲奖** | `effie.org` | APAC Effie, Euro Effie, LatAm Effie, MENA Effie, Greater China Effie, North America Effie, Africa Effie |
| **One Show** | `oneshow.org` | One Show Design, One Show Interactive, One Show Entertainment, One Show Health, One Show Print & Poster, One Show Branded Entertainment, One Show Mobile, One Show ADC (Art Directors Club) |
| **Long Xi 龙玺** | `longxiads.com` (主域 `longxi.com` 已失效,改用此) | 龙玺环球华文广告奖, 龙玺互动, 龙玺户外, 龙玺影视 |
| **Spikes Asia** | `spikes.asia` | Health Spikes, Digital Spikes, Media Spikes, Brand Experience Spikes |
| **ADC Annual Awards (Art Directors Club)** | `adcglobal.org` | Design, Advertising, Interactive, Motion, Photography |
| **D&AD** | `dandad.org` | Black Pencil, Yellow Pencil, Wood Pencil, Graphite Pencil, White Pencil (各品类: Advertising, Design, Digital, Film, Branded Content) |
| **The Webby Awards** | `webbyawards.com` | Websites, Mobile Sites, Apps, Video, Advertising, Social, Podcasts, Games |
| **Clio Awards** | `clios.com` | Clio Health, Clio Sports, Clio Entertainment, Clio Music, Clio Fashion & Beauty, Clio Cannabis |
| **London International Awards (LIA)** | `liaawards.com` | Health & Wellness, Pharma, Music, Entertainment, Branded Entertainment, Digital, Design, Film, Radio, Outdoor, Print, Poster |

**每个奖项每年单独建子目录**: `02_AWARD_SOURCES/Cannes_Lions/Lions_Health/2024/`、`02_AWARD_SOURCES/Cannes_Lions/Creative_Effectiveness/2025/` ...

**v3 修正 (2026-07-01)**: `02_AWARD_SOURCES/` 目录**只写各个年度的获奖清单文档**:
- 每个文档 = 1 个奖项的 1 个子奖项的 1 个年度的 1 个获奖级别 (Grand_Prix / Gold / Silver / Bronze / Shortlist) 的**完整官方获奖名单**
- 文档命名: `<年度>_<子奖项>_<获奖级别>_winners.md` (例: `2025_Creative_Effectiveness_Grand_Prix_winners.md`)
- 数据源: 来自各奖项**官网原始名单** (规则 1 优先 1)
- 清单文档**不**放案例主目录文件 (案例主目录在 `05_CASES/By_Industry/<行业>/<品牌>/<案例名>_<主奖项简写>/`)
- 详细规范见 `02_AWARD_SOURCES/_README.md`

**v3.1 修正 (2026-07-01)**: 实际数据采集发现权威源:
- **各奖项官网新闻/汇总页**: `canneslions.com/news/...` (例: `/news/first-winners-announced-at-the-72nd-cannes-lions-international-festival`, `/news/cannes-lions-announces-2025-final-winners`)
- **Adweek 年度总结**: `adweek.com/.../cannes-lions-YYYY-...` (JS SPA, 需 Chrome 渲染)
- **Adweek 视频汇总**: `adweek.com/creativity/watch-all-the-grand-prix-winners-of-cannes-lions-YYYY/`
- **Contagio 报道**: `contagious.com/en/article/news-and-views/cannes-lions-YYYY-...-winners`
- **lionswork.com**: `lionswork.com/?year=YYYY` (Cannes Lions 官方工作库, JS 重定向, 暂未直访)
- 工具: `04_TOOLCHAIN/04_collect_award_winners.py`

### 优先 2 — 全球广告案例聚合站

- **`www.adsoftheworld.com`** (Ads of the World) — 唯一非官方权威源,主要收录全球优秀广告案例
- 镜像: `https://adsoftheworld.com` (注意:HEAD 请求返回 405,必须用 GET)

### 备用源 — 全球各地区/语言的 Top 10 案例网站

> 这些源**优先作为"内容扩充源"**,而非主收录源。每月轮询,补充奖项官网没覆盖的本土案例。

| 地区 | 网站 |
|---|---|
| 中国 | 数英网 (`digitaling.com`), 梅花网 (`meihua.com`), 广告门 (`admen.cn`), 顶尖文案 (`topys.cn`) |
| 日本 | アドタイ (`ad-today.jp`), ブレーン (`brain-groove.com`), ワコール (`wacoal.jp/campaigns/`) |
| 韩国 | チソン (`chose.co.kr` ?), Campaign Asia (Korea) |
| 印度 | Campaign India (`campaignindia.in`), Bestadsontv (`bestadsontv.com`) |
| 东南亚 | Campaign Asia, Marketech APAC (`marketech-apac.com`) |
| 欧洲 | The Drum (`thedrum.com`), Creative Review (`creativereview.co.uk`), Shots (`shots.net`), Little Black Book (`lbbonline.com`) |
| 北美 | Adweek (`adweek.com`), Advertising Age (`adage.com`), Fast Company (`fastcocreate.com`) |
| 拉美 | Latin Spots (`latinspots.com`), AdLatina (`adlatina.com`) |
| 中东 | Campaign Middle East |
| 俄罗斯/独联体 | Sostav (`sostav.ru`), AdIndex (`adindex.ru`) |

**每月 1 日自动/手动从备用源抓取"过去 30 天新增案例",写入 `05_CASES/By_Source/`。**

### 本地案例来源

> **本节由用户在 `03_LOCAL_SOURCES/LOCAL_SOURCES.md` 手动维护**。
> 当前为占位符,等待用户填入本地路径 / NAS 路径 / 第三方素材库接入信息。

---

## 规则 2 — 案例知识库分类目录树 (v2 修正: 2026-07-01)

### 2.1 分类维度与归档规则 (v3, 2026-07-01 生效)

| 维度 | 用途 | 是否存案例文件 | 维护方式 |
|---|---|---|---|
| **By_Industry** | **默认归档目录** | ✅ **存完整 5 产物** (概述/深度/视频/HTML/PDF + 图片) | 新案例直接建在 `By_Industry/<行业>/<品牌>/<案例名>_<主奖项简写>/` |
| **By_Award** | 按奖项浏览 | ❌ **只存 `_index.md` 案例清单** | 新增/减少案例时, 实时更新 `_index.md` |
| **By_Brand** | 按品牌浏览 | ❌ **只存 `_index.md` 案例清单** | 同上 |
| **By_Source** | 按数据源浏览 | ❌ **只存 `_index.md` 案例清单** | 同上 |
| **By_Year** | (已删除) | ❌ | 年份信息已记录在案例名/清单/HTTP/元数据中, 不作为目录层级 |

**主目录路径格式 (v3)**: `By_Industry/<行业>/<品牌>/<案例名>_<主奖项简写>/`

**重要原则**:
- **案例来源无关性**: 无论案例从哪个来源 (规则 1 的优先 1/优先 2/备用/本地) 抓取, 都按本规则归档到 By_Industry 下, 归档路径**不**反映来源 (来源信息记录在 By_Source/_index.md 和案例元数据中)
- **品牌升 1 级**: 品牌作为目录层级 (1 级), 年份**不**作为目录层级 (降为案例名/元数据的一部分)
- **品牌名标准化**: AXA (不用 A.X.A.)、Coca-Cola (不用 Coca_Cola, 用连字符)、BMW (不是 Bayerische Motoren Werke)

### 2.2 目录结构

```
05_CASES/
├── By_Award/                                # 按奖项分类 (主分类树, 来自规则1优先1)
│   ├── _index.md                            # 案例清单 (实时更新)
│   ├── Cannes_Lions/
│   │   ├── 2024/
│   │   │   ├── Grand_Prix/                # 金狮级 (顶级)
│   │   │   ├── Gold_Lion/                 # 金狮
│   │   │   ├── Silver_Lion/               # 银狮
│   │   │   ├── Bronze_Lion/               # 铜狮
│   │   │   └── Shortlist/                 # 提名
│   │   └── Lions_Health/2024/...
│   ├── Effie_Awards/
│   │   ├── APAC/2024/...
│   │   ├── Greater_China/2024/...
│   │   └── ...
│   ├── One_Show/2024/...
│   ├── DAD/2024/...
│   ├── LIA/2024/...
│   ├── Spikes_Asia/2024/...
│   ├── Clio/2024/...
│   ├── Webby/2024/...
│   ├── ADC/2024/...
│   └── Long_Xi/2024/...
├── By_Source/                               # 按数据源分类 (来自规则1优先1/2)
│   ├── _index.md                            # 案例清单 (实时更新)
│   ├── CannesLions/                         # 案例数据源 (官方大奖)
│   ├── Effie/                               # 案例数据源 (官方大奖)
│   ├── OneShow/                             # 案例数据源 (官方大奖)
│   ├── Longxi/                              # 案例数据源 (官方大奖)
│   ├── Adfest/                              # 案例数据源 (官方大奖)
│   ├── Spikes/                              # 案例数据源 (官方大奖)
│   ├── DandAD/                              # 案例数据源 (官方大奖)
│   ├── LIA/                                 # 案例数据源 (官方大奖)
│   ├── Clio/                                # 案例数据源 (官方大奖)
│   ├── AdsOfTheWorld/                       # 案例数据源 (adsoftheworld)
│   ├── Contagio/                            # 案例数据源 (行业报道)
│   ├── YouTube/                             # 案例数据源 (视频)
│   ├── Vimeo/                               # 案例数据源 (视频)
│   └── ... (备用源: 数英网/梅花网/广告门/顶尖文案 + 全球地区/语言 top10 案例网站)
├── By_Brand/                                # 按品牌分类 (跨奖项聚合)
│   ├── _index.md                            # 案例清单 (实时更新)
│   ├── AXA/                                 # 安盛 (法国保险)
│   ├── Apple/                               # 苹果
│   ├── Nike/                                # 耐克
│   └── ... (其他品牌)
├── By_Industry/                             # 按行业分类 ← 默认归档目录 (v3 修正: 品牌升 1 级)
│   ├── FMCG/
│   ├── Tech/
│   ├── Auto/
│   ├── Finance/
│   ├── Healthcare/
│   ├── Insurance/                            ← 测试案例所在
│   │   └── AXA/                              ← 品牌升 1 级 (v3 修正: 取消年份层级)
│   │       └── Three_Words_Cannes_Grand_Prix/    ← 单一案例目录 (年份记录在案例名中)
│   │           ├── _FOLDER_README.md
│   │           ├── 00_案例概述.md
│   │           ├── 01_案例深度报告.md
│   │           ├── 01_images/                # 案例图片
│   │           ├── 02_videos/                # 案例视频
│   │           ├── 03_videos.md
│   │           ├── 04_archive.html
│   │           └── 04_archive.pdf
│   └── ... (其他行业)
└── (By_Year 已删除)                          # v2/v3 修正: 年份不作为目录层级
```

### 2.3 案例主目录内含 (5 产物)

```
<品牌>_<案例名>_<主奖项简写>/                  # 单一案例目录
├── _FOLDER_README.md                        # 案例目录说明
├── 00_案例概述.md                           # 案例概述 (规则5)
├── 01_案例深度报告.md                       # 案例深度报告 (16节, 规则5)
├── 01_images/                               # 案例图片
│   ├── cover.jpg
│   ├── gallery_01.jpg
│   └── ...
├── 02_videos/                               # 案例视频 (链接清单, 非下载)
│   └── VIDEO_LINKS.md
├── 03_videos.md                             # 视频清单 (YouTube + Vimeo)
├── 04_archive.html                          # 综合档案 HTML (claude 风格)
└── 04_archive.pdf                           # 综合档案 PDF (由 HTML 转换)
```


**重要原则**:
- **单一案例目录命名规则**: `YYYY_Brand_CaseName__Award_Tier/` 例: `2025_Dove_RealBeauty_Lions_Grand_Prix/`
- 同一案例可能被多个奖项收录,**用 `By_Brand/` 主目录,其他分类做软链接** (`mklink /J`)
- 案例内容文件命名 `00/01/02/...` 数字前缀保证排序

---

## 规则 3 — 多元抓取工具链 (SearXNG + Playwright + 代理池)

### 工具栈总览

| 工具 | 角色 | 部署位置 | 健康检查 |
|---|---|---|---|
| **SearXNG** | 元搜索聚合 (不直接抓取,做"找案例 URL"用) | Docker 容器,localhost:8888 (本地优先); 无 Docker 时用公共实例 (searx.be / disroot / sapti / tiekoetter) | `curl http://localhost:8888` 或 verify_stack.py 自动选实例 |
| **Playwright** | 浏览器自动化,处理 JS 渲染页 | Python venv | `python -c "from playwright.sync_api import sync_playwright"` |
| **代理池** | IP 轮换,突破地区封锁和反爬 | WSL2 (建议) | `curl --proxy ...` |
| **yt-dlp** | 视频下载 (YouTube/Vimeo) | Python venv | `yt-dlp --version` |
| **xhtml2pdf** | HTML→PDF 渲染 (纯 Python, 零系统依赖, 兜底方案) | Python venv | `python -c "import xhtml2pdf"` |
| **Playwright (HTML→PDF)** | HTML→PDF 渲染 (推荐, 零外部依赖) | Python venv + chromium | 04_TOOLCHAIN/render_pdf.py |
| **requests + BeautifulSoup4** | 静态页抓取 (首选,轻量) | Python venv | `python -c "import requests, bs4"` |

### 启动顺序 (任何设备部署后必跑)

1. `bash 04_TOOLCHAIN/00_bootstrap.sh` (检查环境, 装 Python 依赖 + Playwright 浏览器)
2. `python 04_TOOLCHAIN/01_verify_stack.py` (验证所有工具可用, SearXNG 失败时自动 fallback 到公共实例)
3. `python 04_TOOLCHAIN/02_proxy_health.py` (代理池存活检测, 失败也继续)
4. **FAIL → 不开始抓取,先修环境 (本地 SearXNG 失败可不修, 用公共实例)**

### 经验沉淀 (来自 via54ADIdeahub `scripts/searxng_expand.py`)

- **adsoftheworld 拒绝 HEAD** → 必须用 `requests.get(url, headers={'User-Agent': 'Mozilla/5.0...'})`
- **数英/梅花有反爬** → 加 `Referer` header, 限速 1 req/2s
- **YouTube/Vimeo 视频 ID 提取** → 正则 `(?<=watch\?v=)[\w-]{11}` (YT) / `(?<=vimeo.com/)\d+` (Vimeo)
- **Cannes Lions 官网搜索参数** → `?award_type=&year=2025&category=`, API 路径 `/api/cases?year=...`
- **Playwright 启动参数** → `headless=True, args=['--disable-blink-features=AutomationControlled']`

详见 `04_TOOLCHAIN/EXPERIENCES.md` (运行后自动追加)。

### 设备迁移指南 (Bootstrap 脚本保证)

任何机器/服务器上,执行以下 3 条命令即可进入案例搜集就绪状态:

```bash
# 1. 复制本 KB 目录(整个 via54_AD_AdCases_KB)
scp -r via54_AD_AdCases_KB/ user@newmachine:~/

# 2. 安装 Python 依赖
pip install -r 04_TOOLCHAIN/requirements.txt
playwright install chromium

# 3. 启动 SearXNG (需要 Docker)
docker run -d --name searxng -p 8888:8080 \
  -e SEARXNG_SECRET=replace-me \
  -v $(pwd)/04_TOOLCHAIN/searxng-settings.yml:/etc/searxng/settings.yml \
  searxng/searxng
```

---

## 规则 4 — 单一案例目录的 5 个标准产物

每个案例最后一级子目录 `_SINGLE_CASE/` 必须包含:

| # | 文件/目录 | 内容 | 命名规范 |
|---|---|---|---|
| 1 | 案例概述 | 综合各奖项标准格式撰写的案例简介 | `00_案例概述.md` |
| 2 | 案例深度报告 | 16 节完整分析 (见规则5) | `01_案例深度报告.md` |
| 3 | 案例图片 | 案例封面 + 内文图片 | `02_images/` |
| 4 | 案例视频 | YouTube / Vimeo 链接清单 (不下载,只记录) | `03_videos/VIDEO_LINKS.md` |
| 5 | 综合档案 | HTML (claude 风格) + 从 HTML 导出的 PDF | `04_archive.html` + `04_archive.pdf` |

**视频来源匹配严格度 (规则5)**: YouTube 搜索时**必须**用 `品牌名+案例名` 精确匹配,首条结果若是官方频道则采用;若首条不是则搜到第 3 条为止,再没有则**在 `VIDEO_LINKS.md` 中标注"未找到匹配视频"**。

**图片获取**: 先查案例官方案例页 → 再查 adsoftheworld 大图 → 都没有则在 `01_案例深度报告.md` 注明"本案例无图片"。

---

## 规则 5 — 文件模板规范

### 5.1 案例概述文件 (`00_案例概述.md`)

> **综合 Cannes Lions / Effie / One Show / D&AD / LIA 五大奖项案例标准撰写格式**:
> - Cannes Lions: 1 段核心创意阐述 + 3-5 段执行细节
> - Effie: 挑战 → 洞察 → 策略 → 执行 → 效果 5 段式
> - One Show: 1 段故事化叙述 + 奖项级别
> - D&AD: 简介 + 类别 + 设计师/代理商
> - LIA: 1 段叙事 + 创意亮点

**合并后模板** (见 `01_TEMPLATES/00_案例概述_template.md`):

```markdown
# [案例名] — [品牌名]

| 字段 | 值 |
|---|---|
| 案例名 | ... |
| 品牌 | ... |
| 行业 | ... |
| 代理公司 | ... |
| 投放国家/地区 | ... |
| 投放年份 | ... |
| 获奖情况 | [Cannes Lions 2025 Grand Prix] [Effie APAC 2025 Gold] ... |
| 主要平台 | YouTube, Instagram, OOH, ... |
| 核心标签 | #品牌重塑 #真实故事 #UGC ... |

## 1. 核心创意 (1 段, 80-150 字)
[用一段话讲清"做了什么"]

## 2. 背景与挑战 (100-200 字)
[品牌当时面临什么市场/营销挑战]

## 3. 洞察 (100-150 字)
[核心人群/文化/市场洞察]

## 4. 策略与执行 (200-300 字)
[怎么做的, 用了哪些创意手法和媒介]

## 5. 效果 (100-200 字, 量化数据)
[获奖情况 + 业务指标 + 社会反响]

## 6. 案例来源链接
- [Cannes Lions 官方案例页](url)
- [adsoftheworld 案例页](url)
- [代理商作品集](url)
- [品牌官方发布](url)
```

### 5.2 案例深度报告文件 (`01_案例深度报告.md`)

> **16 节结构** (见 `01_TEMPLATES/01_案例深度报告_template.md`):

1. **案例概述** (引用 00_案例概述.md 的精简版,200 字内)
2. **基础信息** (品牌/产品/代理/国家/年份/获奖级别/奖项类别)
3. **品牌背景** (品牌历史/定位/市场份额/Slogan)
4. **营销背景** (该案例前品牌营销状态/痛点/竞品动态)
5. **市场背景** (行业大环境/消费者趋势/竞品案例参考)
6. **创意/营销目标** (品牌方 brief 拆解: 认知/转化/品牌资产?)
7. **创意/策略洞察** (核心 idea 从何而来, 文化/人群/技术洞察)
8. **人群/市场洞察** (TA 画像/未被满足的需求/触媒习惯)
9. **执行细节** (执行公司/制作团队/拍摄地点/周期/预算量级)
10. **媒介实现** (媒介组合/投放节奏/媒体占比/技术实现)
11. **创意物料** (视频/海报/H5/线下装置 等所有产出的形式清单)
12. **执行成果** (KPI 完成情况/获奖清单/媒体露出)
13. **效果与证据** (数据/调研/第三方背书/Case Study Video 链接)
14. **文化与社会影响** (对行业/文化议题/社会讨论的推动)
15. **案例来源链接** (完整 URL 列表)
16. **案例视频链接** (YouTube/Vimeo 精确匹配后的链接 + 验证状态)

### 5.3 案例图片 (`02_images/`)

- **cover.jpg**: 案例封面图 (官网/adsoftheworld 大图, 优先横版 16:9)
- **gallery_NN.jpg**: 内文配图, 数字编号 01/02/...
- **缺失处理**: 在 `01_案例深度报告.md` 第 11 节"创意物料"末尾写一句 `> ⚠️ 本案例未找到图片素材, 仅以文字记录`

### 5.4 案例视频 (`03_videos/VIDEO_LINKS.md`)

```markdown
# 案例视频清单

## YouTube
- 链接: https://www.youtube.com/watch?v=XXXX
- 标题: [官方频道名] [视频标题]
- 验证: ✅ 已核对 (品牌名+案例名匹配)
- 上传日期: YYYY-MM-DD
- 时长: MM:SS

## Vimeo
- 链接: https://vimeo.com/XXXX
- 标题: ...
- 验证: ✅ 已核对
- 嵌入代码: <iframe src="https://player.vimeo.com/video/XXXX" ...></iframe>

## 验证规则
- 搜索关键词: `"<品牌名>" "<案例名>"`
- 来源优先级: 品牌官方 YouTube > 代理商作品集 > 案例官方页内嵌
- 未找到处理: ⚠️ 在下方"未匹配"区块写明
```

### 5.5 HTML + PDF 综合档案

- **`04_archive.html`**: Claude 风格设计 (大量留白、衬线/无衬线混排、配色克制、代码块/表格/引述样式精致)
- **`04_archive.pdf`**: 由 `04_archive.html` 用 `weasyprint` 导出

**HTML 模板规范**:
- 字体: `Inter` (UI) + `Source Serif Pro` (正文) + `JetBrains Mono` (代码)
- 配色: 背景 `#fafaf7`、主文 `#1a1a1a`、强调 `#c2410c` (品牌色) — 避免饱和度过高
- 排版: max-width 720px 居中, 行高 1.7, 段落间距 1.5em
- 图片: 100% 宽度 + caption
- 视频: iframe 嵌入 (不下载)
- 模板: `01_TEMPLATES/04_archive_html_template.html`

**HTML→PDF 命令** (优先 Playwright, 失败 fallback weasyprint):
```bash
python 04_TOOLCHAIN/render_pdf.py 04_archive.html 04_archive.pdf
```

---

## 规则执行检查清单 (抓取每个案例前自检)

- [ ] 案例来源属于规则 1 的"优先 1"还是"优先 2"? (优先 1 优先收录)
- [ ] 案例目录路径符合规则 2 的分类树?
- [ ] 工具链 (SearXNG/Playwright/代理) 全部健康?
- [ ] 案例目录下 5 个标准产物齐全?
- [ ] 概述文件和深度报告都按规则 5 模板?
- [ ] 视频链接经过品牌名+案例名精确匹配验证?
- [ ] HTML 综合档案已生成, PDF 已从 HTML 导出?

**未通过自检 → 不算完成, 不写入 `99_LOGS/` 完成记录。**
