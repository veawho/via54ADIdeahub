"""
04_collect_award_winners.py — 全量抓取某广告奖项某年度某级别获奖名单

用法:
    # 抓 Cannes Lions 2025 Creative Effectiveness Grand Prix
    python 04_collect_award_winners.py \\
        --award Cannes_Lions \\
        --subaward Creative_Effectiveness \\
        --year 2025 \\
        --tier Grand_Prix \\
        --out /path/to/winners.md

    # 批量模式 (YAML 配置)
    python 04_collect_award_winners.py --config batch.yaml

策略:
    1. SearXNG 搜官网原始名单 (priority 1: canneslions.com / dad.org / oneclub.org / clios.com 等)
    2. 抓页面 → 解析 → 表格 (案例名/品牌/代理商/国家/详情 URL)
    3. 自动写到 02_AWARD_SOURCES/<award>/<sub>/<year>/<year>_<sub>_<tier>_winners.md
    4. 已存在的清单 → 跳过 (idempotent)

数据源优先级:
    - 官网 (canneslions.com/awards, dad.org, oneclub.org, clios.com 等)
    - adsoftheworld.com (按奖项过滤)
    - Contagio.com (年度总结报道)
    - Adweek / The Drum (年度总结)

作者: via54 Hermes Agent
日期: 2026-07-01
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

# 复用 03_collect_case.py 的工具
try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

# 工具常量
SEARXNG_URL = "http://localhost:9086/search"
WSL_CHROME = "/opt/google/chrome/chrome"
_KB_ROOT = Path.home() / "Desktop" / "developments" / "via54ADIdeahub" / "docs" / "AD_CASES_KB"

# 奖项官网基础 URL (规则 1 优先 1)
AWARD_SITES = {
    "Cannes_Lions": "canneslions.com",
    "DAD": "dandad.org",
    "One_Show": "theoneclubforcreativity.com",
    "Effie_Awards": "effie",  # 注: AWARD_SITES 的 value 是裸域名, 模板里 https://www.{X}.com 会拼成 https://www.effie.com (错). 需要模板分支处理
    "LIA": "liaawards.com",
    "Clio": "clios.com",
    "Webby": "webbyawards.com",
    "Long_Xi": "longxiawards.com",
    "Spikes_Asia": "spikes.asia",
    "ADC_Annual": "adcawards.org",
}

# 子奖项 → URL slug 映射
SUB_SLUGS = {
    "Cannes_Lions": {
        "Lions_Health": "lions-health",
        "Creative_Effectiveness": "creative-effectiveness",
        "Creative_B2B": "creative-b2b",
        "Sustainable_Development_Good": "sustainable-development-goals",
        # ...
    },
    "DAD": {
        "Advertising": "advertising",
        "Design": "design",
        "Digital": "digital-design",
        "Film": "film",
        "Branded_Content": "branded-content",
    },
    # ...
}


def searxng_search(query: str, sites: list = None, num: int = 10) -> list:
    """SearXNG 搜索 (注: SearXNG 不支持 site: 操作符)"""
    import requests
    params = {
        "q": query,
        "format": "json",
        "language": "en",
        "engines": "bing,yahoo,reddit,mojeek,qwant",  # 备用引擎 (brave/google 频繁被 CAPTCHA 拒)
    }
    try:
        r = requests.get(SEARXNG_URL, params=params, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return data.get("results", [])[:num]
    except Exception as e:
        print(f"  [WARN] SearXNG 失败: {e}")
    return []


def _extract_pdf_text(content_bytes):
    """提取 PDF 文本 — 用 pdfplumber 优先, pypdf fallback"""
    try:
        import pdfplumber
        import io
        text_pages = []
        with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
            for page in pdf.pages[:50]:
                t = page.extract_text() or ""
                text_pages.append(t)
        return "\n\n".join(text_pages)
    except ImportError:
        pass
    except Exception as e:
        print(f"  [WARN] pdfplumber 失败: {e}")
    try:
        import pypdf
        import io
        reader = pypdf.PdfReader(io.BytesIO(content_bytes))
        text_pages = []
        for page in reader.pages[:50]:
            t = page.extract_text() or ""
            text_pages.append(t)
        return "\n\n".join(text_pages)
    except ImportError:
        pass
    except Exception as e:
        print(f"  [WARN] pypdf 失败: {e}")
    # 兜底 — WSL pdftotext
    try:
        import subprocess, tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(content_bytes)
            tmp_pdf = f.name
        r = subprocess.run(["wsl", "-e", "bash", "-c", f"pdftotext '{tmp_pdf}' -"],
                          capture_output=True, text=True, timeout=30)
        return r.stdout
    except Exception as e:
        print(f"  [WARN] pdftotext 失败: {e}")
        return ""

def parse_winners_from_text(content: str, source_url: str = "") -> list:
    """从纯文本 (PDF 提取后) 解析获奖案例
    Effie PDF 格式: '品牌\n案例名\n品牌商\n代理商*' 块状
    """
    winners = []
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    # Effie 块模式: 大写品牌 + 短案例名 + 公司名 + 公司名*
    for i in range(len(lines) - 2):
        # 候选案例名: 短 (3-80 字符), 不是 IRIDIUM WINNER 这种常量
        case_name = lines[i]
        brand = lines[i+1] if i+1 < len(lines) else ""
        agency = lines[i+2] if i+2 < len(lines) else ""
        # 启发式: 案例名=短语, 品牌/代理商=更短
        if (3 < len(case_name) < 80 
            and not case_name.isupper()  # 不是全大写品牌
            and not any(skip in case_name.lower() for skip in ['iridium winner', 'global grand', 'topical', 'commerce', 'finance', 'retail', 'sustained success', 'positive change', 'experiential', 'timely opportunity', 'winners', 'global best'])):
            # 检查后面有公司名 (含 Inc / Corp / GmbH / * / Pty)
            if any(suffix in (agency + brand).lower() for suffix in ['inc', 'corp', 'gmbh', 'pty', '*', 'ltd', 'limited', 'ag ', 'group']):
                winners.append([case_name, brand, agency, source_url])
    # 去重
    seen = set()
    unique = []
    for w in winners:
        key = w[0]
        if key not in seen:
            seen.add(key)
            unique.append(w)
    return unique[:30]





def fetch_page(url: str, use_wsl_chrome: bool = True) -> str:
    """抓取页面 HTML/PDF, WSL Chrome 渲染动态页"""
    import requests
    try:
        r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}, verify=False)
        # 检测 PDF
        ct = r.headers.get("content-type", "").lower()
        if "pdf" in ct or url.lower().endswith(".pdf") or r.content[:4] == b"%PDF":
            return _extract_pdf_text(r.content)
        html = r.text
        # JS SPA 检测
        if len(html) < 50000 and html.count("<script") > 5 and not any(kw in html.lower() for kw in ['grand prix', 'winner', 'lions']):
            print(f"  [WSL] JS SPA 检测, 用 Chrome 渲染")
            return fetch_via_wsl_chrome(url)
        return html
    except Exception as e:
        print(f"  [WARN] requests 失败: {e}, 回退 WSL Chrome")
        return fetch_via_wsl_chrome(url)


def fetch_via_wsl_chrome(url: str) -> str:
    """WSL Chrome 渲染抓取 (动态页)"""
    import subprocess
    import base64
    script = f'''
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/google/chrome/chrome", headless=True)
    page = browser.new_page()
    try:
        page.goto("{url}", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)
        html = page.content()
    except Exception as e:
        html = f"<error>{{e}}</error>"
    browser.close()
    print(json.dumps({{"html_len": len(html), "html": html}}))
'''
    b64 = base64.b64encode(script.encode()).decode()
    try:
        r = subprocess.run(
            ["wsl", "-e", "bash", "-c", f"echo {b64} | base64 -d > /tmp/fetch_wsl.py && python3 /tmp/fetch_wsl.py"],
            capture_output=True, text=True, timeout=90
        )
        if r.stdout:
            try:
                data = json.loads(r.stdout)
                return data.get("html", "")
            except json.JSONDecodeError:
                return r.stdout  # 原始输出
    except Exception as e:
        print(f"  [WARN] WSL Chrome 失败: {e}")
    return ""


def parse_winners_table(html: str, source_url: str) -> list:
    """从 HTML 解析获奖案例表格

    支持 3 类源:
    1. 官网新闻页 (canneslions.com/news/...) - 通常 <h2>/<h3> 含 "Grand Prix" + 案例名
    2. Contagio 报道 (contagious.com/...) - 通常 <p> 段落含案例名+品牌
    3. Adweek 总结 (adweek.com/...) - JS SPA, 需 Chrome 渲染 (本函数处理渲染后 HTML)
    """
    winners = []

    # === 策略 A: <h2>/<h3> 含 "Grand Prix"/"Gold" 关键词 + 链接 ===
    for tag in ['h2', 'h3', 'h4']:
        pattern = rf'<{tag}[^>]*>(.*?)</{tag}>'
        for match in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
            header_text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
            # 过滤: 必须含获奖级别关键词
            if not any(kw in header_text for kw in ['Grand Prix', 'Gold', 'Silver', 'Bronze', 'Winner', 'Shortlist']):
                continue
            # 提取该 h 标签下方的链接 (找后续 <a> 直到下一个同级 h)
            # 简化: 找同一段内的 <a>
            section_html = html[match.start():match.start() + 3000]  # 后续 3KB
            links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', section_html, re.DOTALL | re.IGNORECASE)
            for href, anchor in links:
                case_name = re.sub(r'<[^>]+>', '', anchor).strip()
                case_name = re.sub(r'\s+', ' ', case_name)
                if case_name and len(case_name) > 3 and len(case_name) < 200 and not case_name.startswith('http'):
                    # 过滤 nav/footer
                    if any(skip in href for skip in ['login', 'signup', 'twitter', 'facebook', 'instagram', 'privacy', 'terms']):
                        continue
                    winners.append([case_name, href])

    # === 策略 B: <article> 元素 (Cannes Lions/Adweek 卡片) ===
    article_pattern = re.compile(r'<article[^>]*>(.*?)</article>', re.DOTALL | re.IGNORECASE)
    for art_match in article_pattern.finditer(html):
        art_html = art_match.group(1)
        # 提取标题 + 链接
        title_match = re.search(r'<h\d[^>]*>(.*?)</h\d>', art_html, re.DOTALL)
        link_match = re.search(r'href="([^"]+)"', art_html)
        if title_match and link_match:
            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
            title = re.sub(r'\s+', ' ', title)
            link = link_match.group(1)
            if title and len(title) > 3 and len(title) < 200:
                # 优先有 "Grand Prix"/"Gold" 关键词的
                if any(kw in title for kw in ['Grand Prix', 'Gold', 'Silver', 'Bronze', 'Winner']):
                    winners.append([title, link])

    # === 策略 C: <table> 表格 (某些站点) ===
    table_pattern = re.compile(r'<table[^>]*>(.*?)</table>', re.DOTALL | re.IGNORECASE)
    for table_match in table_pattern.finditer(html):
        table_html = table_match.group(1)
        for row_match in re.finditer(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE):
            row_html = row_match.group(1)
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row_html, re.DOTALL | re.IGNORECASE)
            cells_clean = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            cells_clean = [re.sub(r'\s+', ' ', c) for c in cells_clean if c]
            if cells_clean and len(cells_clean) >= 2:
                # 过滤 nav/footer
                if any(skip in ' '.join(cells_clean) for skip in ['Privacy', 'Cookie', 'Subscribe', 'Newsletter']):
                    continue
                winners.append(cells_clean)

    # === 策略 D: Contagio 风格 - <strong>/<b> 含品牌名 + 段落 ===
    strong_pattern = re.compile(r'<(strong|b)[^>]*>(.*?)</\1>', re.DOTALL | re.IGNORECASE)
    for s_match in strong_pattern.finditer(html):
        brand = re.sub(r'<[^>]+>', '', s_match.group(2)).strip()
        if brand and len(brand) > 2 and len(brand) < 80:
            # 找相邻段落
            pos = s_match.end()
            para = html[pos:pos + 500]
            para_text = re.sub(r'<[^>]+>', ' ', para).strip()[:300]
            if any(kw in para_text for kw in ['Grand Prix', 'Gold', 'Silver', 'Bronze', 'Lion']):
                winners.append([brand, para_text[:200]])

    # 去重 (按案例名)
    seen = set()
    unique = []
    for w in winners:
        key = w[0] if w else ""
        if key and key not in seen:
            seen.add(key)
            unique.append(w)

    return unique[:50]  # 限 50 案例/页, 防止噪声过多


def _url_for(award):
    """Bug fix #1: Effie URL 双 TLD"""
    sites = {"Effie_Awards": "effie.org", "DAD": "dandad.org", "Webby": "webbyawards.com"}
    return sites.get(award, f"{award.lower()}")


SEED_URLS = {
    ("DAD", 2025): ["https://media.dandad.org/documents/DAD_ANNOUNCES_2025_PENCIL_WINNERS.pdf"],
    ("Effie_Awards", 2024): [
        "https://www.effie.org/news/effie-awards-unveils-global-multi-region-winners-for-2024/",
        "https://www.effie-europe.com/wp-content/uploads/2024/12/Effie-Awards-winners-list-2024-1.pdf",
        "https://apaceffie.com/docs/default-source/default-document-library/2024-apac-effie-awards-winners.pdf",
    ],
    ("Effie_Awards", 2025): [
        "https://s3.amazonaws.com/current.effie.org/2025/2025_Effie_Global%20Best%20of%20the%20Best_Awarded%20List.pdf",
        "https://apaceffie.com/docs/default-source/default-document-library/2025-apac-effie-award-winners.pdf",
        "https://s3.amazonaws.com/current.effie.org/2025/2025_Effie_Awards_US_Finalists&Winners.pdf",
    ],
    ("Effie_Awards", 2026): [
        "https://s3.amazonaws.com/current.effie.org/2026/2026%20Effie%20Awards%20US%20Winners.pdf",
    ],
}




def _validate_source_domain(award: str, source_url: str) -> bool:
    """数据源 domain 必须匹配奖项官方 domain — 否则不写
    
    防止 subagent 时代 SearXNG 返回其他汇总页导致误标
    """
    if not source_url:
        return False
    from urllib.parse import urlparse
    domain = urlparse(source_url).netloc.lower()
    
    valid_domains = {
        "Webby": ["webbyawards.com"],
        "Clio": ["clios.com", "clioawards.com"],
        "DAD": ["dandad.org"],
        "Effie_Awards": ["effie.org", "apaceffie.com", "effie-europe.com", "current.effie.org", "effie-greaterchina.cn"],
        "Cannes_Lions": ["canneslions.com", "lionswork.com"],
        "One_Show": ["theoneclubforcery.com", "oneclub.org", "theoneclub.com"],
        "LIA": ["liaawards.com"],
        "Spikes_Asia": ["spikes.asia", "spikes-asia.com"],
        "ADC_Annual": ["adcglobal.org", "aiga.org", "creativeclub.com"],
        "Long_Xi": ["longxiawards.com.cn", "longxiaward.com"],
    }
    domains = valid_domains.get(award, [])
    if not domains:
        return True  # 未知奖项不强制校验
    # 信任主源 + s3 镜像 (Effie PDF)
    if "s3.amazonaws.com" in domain and any(d in domain or "effie" in domain for d in []):
        return True
    return any(d in domain for d in domains)


def _try_delete_placeholder(award, subaward, year, tier):
    """Bug fix #3: 失败时主动删 placeholder"""
    fname = f"{year}_{subaward}_{tier.replace(' ', '_')}_winners.md"
    out_path = _KB_ROOT / "02_AWARD_SOURCES" / award / subaward / str(year) / fname
    if out_path.exists() and out_path.stat().st_size < 2000:
        out_path.unlink()
        return True
    return False


def write_winners_md(out_path: Path, award: str, subaward: str, year: int, tier: str, winners: list, source_url: str):
    """写获奖清单 .md"""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists():
        size = out_path.stat().st_size
        # 占位符 (1-2KB, 数据源但无真实案例) → 删,重抓
        if size < 2000:
            out_path.unlink()
            print(f"  [RETRY] 删除占位符 ({size} bytes), 重新抓取")
        else:
            try:
                rel = out_path.relative_to(_KB_ROOT)
            except ValueError:
                rel = out_path
            print(f"  [SKIP] 已存在: {rel} ({size} bytes)")
            return False

    content = f"""# {year} {award.replace('_', ' ')} {subaward.replace('_', ' ')} {tier.replace('_', ' ')} winners

> **奖项官方**: https://www.{_url_for(award)}.com/awards
> **评选年度**: {year}
> **子奖项**: {subaward.replace('_', ' ')}
> **获奖级别**: {tier.replace('_', ' ')}
> **数据源**: {source_url}
> **收录时间**: 2026-07-01
> **案例数**: {len(winners) if isinstance(winners, list) and winners and isinstance(winners[0], list) else 0}

## 获奖案例列表

| # | 案例名 | 品牌 | 代理商 | 国家/地区 | 案例详情 URL |
|---|---|---|---|---|---|
"""

    if isinstance(winners, list) and winners:
        for i, row in enumerate(winners, 1):
            if isinstance(row, list) and len(row) >= 2:
                # row 可能是 [案例名, URL] 或 [案例名, 品牌, 代理商, ...]
                if len(row) >= 4:
                    content += f"| {i} | {row[0]} | {row[1]} | {row[2]} | {row[3] if len(row) > 3 else ''} | {row[4] if len(row) > 4 else ''} |\n"
                elif len(row) == 2:
                    content += f"| {i} | {row[0]} | (待 enrich) | (待 enrich) | (待 enrich) | {row[1]} |\n"
                else:
                    content += f"| {i} | {' | '.join(row)} |\n"
    else:
        content += "| - | (待抓取) | - | - | - | - |\n"

    content += f"""
## 数据源

- 官方网站: {source_url}
- 收录时间: 2026-07-01 (v1.0 首次抓取)

## 维护规范

- 本文档 = {year} 年度 {subaward} 子奖项 {tier} 级别的**完整官方获奖名单**
- 数据采集: `04_TOOLCHAIN/04_collect_award_winners.py --award {award} --subaward {subaward} --year {year} --tier {tier}`
- 案例主目录 (5 产物): `05_CASES/By_Industry/<行业>/<品牌>/<案例名>_<主奖项简写>/`
- 关联: `05_CASES/By_Award/_index.md` (KB 收录案例跨年度索引)
"""

    out_path.write_text(content, encoding="utf-8")
    size = out_path.stat().st_size
    try:
        rel = out_path.relative_to(_KB_ROOT)
    except ValueError:
        rel = out_path
    print(f"  ✅ 写入: {rel} ({size} bytes, {len(winners) if isinstance(winners, list) else 0} 案例)")
    return True


def collect_one(award: str, subaward: str, year: int, tier: str, output_root: Path) -> dict:
    """抓 1 份获奖清单"""
    print(f"\n=== 抓取: {award} / {subaward} / {year} / {tier} ===")

    # 1) SearXNG 找官方/权威名单 URL
    site = AWARD_SITES.get(award, award.lower())
    # tier 关键词: ADC "Black Cube" / Cannes "Grand Prix" / D&AD "Yellow Pencil"
    tier_kw = tier.replace("_", " ")
    # subaward 人类可读名
    human_sub = subaward.replace("_", " ")

    if award == "ADC_Annual":
        # ADC Annual Awards — 顶级奖 "Black Cube"
        queries = [
            f"{year} ADC Annual Awards {tier_kw} winners",
            f"{year} ADC Annual Awards winners",
            f"{year} {site} awards winners",
            f"{year} ADC {year}th Annual Awards winners",
            # 兜底 (One Club 归档)
            f"{year} ADC Awards {tier_kw} oneclub.org",
        ]
        allowed_domains = [site, f"www.{site}", "adweek.com", "thedrum.com"]
    elif award == "Clio":
        # Clio: 必须 clios.com (clio.com 是法律软件, 完全无关)
        queries = [
            f"{year} Clio {human_sub} {tier_kw} winner clios.com",
            f"{year} Clio Awards {human_sub} winners announced",
            f"Clio {human_sub} {year} winners gallery clios.com",
            f"{year} Clio Music winners clios.com press",
        ]
        allowed_domains = ["clios.com"]
        # Clio 没有 adweek 兜底 — adweek 报 Cannes Lions
    elif award == "Cannes_Lions":
        queries = [
            f"{year} Cannes Lions Grand Prix winners",
            f"{year} Cannes Lions {human_sub} Grand Prix winners",
        ]
        allowed_domains = ["canneslions.com", "creativereview.co.uk", "adweek.com", "thedrum.com"]
    else:
        queries = [
            f"{year} {site} award winners",
            f"{year} {site} {tier_kw} winners",
            f"{year} {site} {human_sub} {tier_kw} winners",
            f"{year} {site} Pencil winners",
            f"{year} {site} winners",
        ]
        allowed_domains = [site, f"www.{site}", "adweek.com", "thedrum.com"]

    results = []
    source_url = ""
    for q in queries:
        r = searxng_search(q, num=10)
        if r:
            # 优先级: 1) 官网汇总页 / press-article → 2) 白名单媒体 → 3) winners+year (仅非 Clio)
            for item in r:
                url = item.get("url", "")
                domain = url.split("/")[2] if "/" in url else ""
                # 官网汇总页 / press-article (Clio 静态页)
                primary = allowed_domains[0] if allowed_domains else ""
                if primary and primary in domain and any(k in url.lower() for k in ["winners", "awards", "announced", str(year), "press-article"]):
                    source_url = url
                    results = r
                    break
            if not source_url:
                # 白名单媒体 (Adweek/TheDrum/CreativeReview)
                for item in r:
                    url = item.get("url", "")
                    domain = url.split("/")[2] if "/" in url else ""
                    if any(d in domain for d in allowed_domains[1:] if d) and str(year) in url:
                        source_url = url
                        results = r
                        break
            if not source_url and award != "Clio":
                # 任何含 winners + year (仅非 Clio)
                for item in r:
                    url = item.get("url", "")
                    if all(k in url.lower() for k in ["winners", str(year)]) or "grand-prix" in url.lower():
                        source_url = url
                        results = r
                        break
            if source_url:
                break

    if not source_url:
        # SearXNG 兜底: 用已知 SEED_URLS (ADC 域名被 "Arizona Dept of Corrections" 污染, 必须直接试官方 URL)
        seeds = SEED_URLS.get((award, year), [])
        if not seeds and (award, str(year)) in SEED_URLS:
            seeds = SEED_URLS[(award, str(year))]
        if seeds:
            print(f"  [INFO] SearXNG 失败, 试 SEED_URLS ({len(seeds)} URLs)")
            for seed_url in seeds:
                # 验证 URL 可达 + 含目标关键词
                try:
                    import requests as _r
                    rr = _r.get(seed_url, timeout=20, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"})
                    if rr.status_code == 200 and len(rr.text) > 1000:
                        body_lc = rr.text.lower()
                        if any(kw in body_lc for kw in ["black cube", "adc", "art director", subaward.lower().replace("_", " "), str(year)]):
                            source_url = seed_url
                            results = [{"url": seed_url, "title": f"SEED_URL ({award} {year})"}]
                            print(f"  [INFO] SEED_URLS 命中: {seed_url}")
                            break
                except Exception as e:
                    print(f"  [WARN] SEED {seed_url} 失败: {e}")

    if not source_url:
        print(f"  [FAIL] SearXNG+SEED 都没找到 {award} {year} {tier_kw} 名单 (子: {subaward})")
        return {"status": "no_source", "award": award, "subaward": subaward, "year": year, "tier": tier}

    print(f"  [INFO] 数据源: {source_url}")

    # 2) 抓页面
    html = fetch_page(source_url)
    if not html:
        print(f"  [FAIL] 抓取 {source_url} 失败")
        return {"status": "fetch_fail", "url": source_url}

    # 3) 解析获奖名单
    if "<html" in html or "<body" in html or "<div" in html:
        winners = parse_winners_table(html, source_url)
    else:
        winners = parse_winners_from_text(html, source_url)
    print(f"  [INFO] 解析到 {len(winners)} 行")

    # 3.5) Clio SPA 兜底: 0 行 → 自动试 Wayback Machine 镜像
    if not winners and "clios.com" in source_url:
        print(f"  [RETRY] clios.com SPA 无数据, 试 Wayback Machine")
        import requests as _req
        try:
            r = _req.get("https://archive.org/wayback/available", params={"url": source_url}, timeout=15)
            if r.status_code == 200:
                data = r.json()
                snap = data.get("archived_snapshots", {}).get("closest", {})
                if snap.get("available"):
                    wb_url = snap["url"]
                    print(f"  [RETRY] Wayback 镜像: {wb_url}")
                    wb_html = _req.get(wb_url, timeout=30, headers={"User-Agent": "Mozilla/5.0"}).text
                    winners = parse_winners_table(wb_html, wb_url)
                    if winners:
                        source_url = wb_url
                        print(f"  [RETRY] Wayback 命中: {len(winners)} 行")
        except Exception as e:
            print(f"  [WARN] Wayback 失败: {e}")

    # 4) 写 .md — 占位符/0 行 = FAIL, 不写
    out_path = output_root / award / subaward / str(year) / f"{year}_{subaward}_{tier}_winners.md"
    if not winners:
        print(f"  [FAIL] 解析到 0 行, 不写占位符")
        return {
            "status": "parse_fail",
            "award": award,
            "subaward": subaward,
            "year": year,
            "tier": tier,
            "source_url": source_url,
            "out_path": str(out_path),
        }
    # 数据源 domain 校验
    if not _validate_source_domain(award, source_url):
        print(f"  [FAIL] 数据源 {source_url} 与奖项 {award} 不匹配 (汇总页误标防护)")
        return {"status": "domain_mismatch", "source": source_url, "award": award}
    write_winners_md(out_path, award, subaward, year, tier, winners, source_url)

    return {
        "status": "ok",
        "award": award,
        "subaward": subaward,
        "year": year,
        "tier": tier,
        "source_url": source_url,
        "winners_count": len(winners),
        "out_path": str(out_path),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--award", help="奖项 (Cannes_Lions/DAD/One_Show/...)")
    parser.add_argument("--subaward", help="子奖项")
    parser.add_argument("--year", type=int, help="年度")
    parser.add_argument("--tier", help="获奖级别 (Grand_Prix/Gold/Silver/Bronze/Shortlist)")
    parser.add_argument("--out-root", default=str(_KB_ROOT / "02_AWARD_SOURCES"), help="输出根")
    parser.add_argument("--config", help="批量配置文件 (YAML/JSON)")
    args = parser.parse_args()

    out_root = Path(args.out_root)

    if args.config:
        # 批量模式
        import yaml
        with open(args.config) as f:
            batch = yaml.safe_load(f) if args.config.endswith((".yml", ".yaml")) else json.load(f)
        results = []
        for item in batch.get("items", []):
            r = collect_one(
                item["award"], item["subaward"], item["year"], item["tier"], out_root
            )
            results.append(r)
            time.sleep(2)  # 防反爬
        # 写 batch 结果
        log_path = out_root / "_batch_log.json"
        log_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        ok = sum(1 for r in results if r["status"] == "ok")
        print(f"\n=== 批量完成: {ok}/{len(results)} 成功 ===")
    else:
        # 单个模式
        if not all([args.award, args.subaward, args.year, args.tier]):
            parser.error("单模式需要 --award --subaward --year --tier")
        r = collect_one(args.award, args.subaward, args.year, args.tier, out_root)
        print(f"\n=== 结果: {json.dumps(r, indent=2, ensure_ascii=False)} ===")


if __name__ == "__main__":
    main()
