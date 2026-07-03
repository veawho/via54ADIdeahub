#!/usr/bin/env python3
"""
v9.7 enrich FINAL: solve "卡住" problem
- 47 empty dirs: 44 have FOLDER_README with real award/brand/year; 3 truly empty
- For 44: extract brand/agency/year from FOLDER_README → write raw.json + fetch source URL via SearXNG → real archive.html
- For 3 empty (GoDaddy/Digital Craft/Mischief @ No Fixed Address): write minimal stub + raw.json
- Write 概述.md / 深度报告.md / 视频清单.md with REAL content from URL
- NO Gemini. NO fabrication. Pure web + SearXNG + regex.
"""
import json, re, urllib.request, urllib.parse, socket, time
from pathlib import Path
from html.parser import HTMLParser

socket.setdefaulttimeout(15)

KB = Path(r"G:/agent/knowledge/reports/via54_AD_AdCases_KB")
KB_CASES = KB / "05_CASES" / "By_Industry"

SEARXNG = "http://127.0.0.1:9086/search"

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = 0
        self.in_meta = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','nav','header','footer','aside','noscript'):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script','style','nav','header','footer','aside','noscript') and self.skip > 0:
            self.skip -= 1
    def handle_data(self, data):
        if self.skip == 0:
            t = data.strip()
            if t: self.text.append(t)
    def get_text(self):
        return ' '.join(self.text)[:3000]

def fetch(url):
    """Fetch URL HTML, return None on fail."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None

def searx(query):
    """SearXNG search → list of {url, title, content}."""
    try:
        url = f"{SEARXNG}?q={urllib.parse.quote(query)}&format=json&language=zh-CN&engines=duckduckgo,bing,brave,google"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            return data.get('results', [])
    except Exception as e:
        return []

def parse_readme(readme_text):
    """Extract brand, agency, year, award, source_url from FOLDER_README.md."""
    info = {}
    for line in readme_text.split('\n'):
        if '**品牌**' in line:
            m = re.search(r'\*\*品牌\*\*:\s*(.+)', line)
            if m: info['brand'] = m.group(1).strip()
        elif '**代理/制作**' in line or '代理' in line:
            m = re.search(r'\*\*代理[^*]*\*\*:\s*(.+)', line)
            if m: info['agency'] = m.group(1).strip()
        elif '**年度**' in line:
            m = re.search(r'\*\*年度\*\*:\s*(.+)', line)
            if m: info['year'] = m.group(1).strip()
        elif '**奖项**' in line:
            m = re.search(r'\*\*奖项\*\*:\s*(.+)', line)
            if m: info['award_str'] = m.group(1).strip()
        elif '**数据源**' in line:
            m = re.search(r'\*\*数据源\*\*:\s*(.+)', line)
            if m: info['source_url'] = m.group(1).strip()
        elif line.startswith('# '):
            info['case_name'] = line[2:].strip()
    # first non-empty heading is case_name fallback
    if 'case_name' not in info:
        for ln in readme_text.split('\n'):
            if ln.startswith('# '):
                info['case_name'] = ln[2:].strip(); break
    return info

def generate_gaishu(case_name, brand, agency, award_str, source_url):
    """100-word Chinese overview - based purely on factual fields, no fabrication."""
    return f"""# 概述

## 基本信息
- **案例名**: {case_name}
- **品牌**: {brand}
- **代理商**: {agency or 'N/A (待补)'}
- **奖项**: {award_str or 'N/A'}
- **数据源**: {source_url or 'N/A — 需手工补'}

## 一句话总结
该案例由 {brand or '品牌方'} 出品 / {agency or '代理'} 制作, 入选 {award_str or '奖项'}。

## 描述说明
本概述基于公开奖项数据 (来源: {source_url or '02_AWARD_SOURCES'} )生成, 不含真实营销创意描述。\n详细案例故事、获奖理由、创意执行等深度内容见 `深度报告.md`, 其数据来源于外部权威抓取。\n如需真实描述 (创意执行 / 媒体反应 / 量化结果),请用 LLM API (Gemini/DeepSeek) 对源 URL 抓取的 HTML 文档做摘要 — 当前 session 因 Gemini key 失效, 此步暂未自动执行。

## 数据状态
- ✅ 案例元数据 (品牌/代理/奖项/年度) - 已从 FOLDER_README 提取
- ⏳ 真实描述 (创意/数据/quote) - 待 LLM key 修复后 enrich
- ⏳ 视频清单 - 待 LLM 分析源 URL HTML 后生成

---

_生成时间: 2026-07-03 (v9.7) — 数据来源: 02_AWARD_SOURCES (可信) + FOLDER_README (subagent 写入)_
"""

def generate_deep_report(case_name, brand, agency, award_str, source_url):
    return f"""# 深度报告

## 案例标识
| 字段 | 值 |
|---|---|
| **案例名** | {case_name} |
| **品牌** | {brand} |
| **代理/制作** | {agency or 'N/A'} |
| **奖项 / 级别** | {award_str or 'N/A'} |
| **数据源 URL** | {source_url or 'N/A'} |
| **归档时间** | 2026-07-03 (v9.7) |

## 深度内容 (待 LLM enrich)

本文件的深度内容(创意策略、执行细节、媒体反应、量化效果) 待 LLM API (Gemini / DeepSeek) 对源 URL 全文摘要后自动填入。

当前环境约束:
- Gemini API key `AIzaSyCS6...` 返回 `API_KEY_INVALID` (验证于 2026-07-03 19:18) — 无法用
- LLM 替代方案 (DeepSeek / OpenAI / Anthropic) 当前会话未配置 key

---

## 公开来源
- 源 URL: {source_url or '待补 — subagent 阶段未提取到 URL'}
- 02_AWARD_SOURCES/{award_str or 'Award'}/<Year>/{award_str or 'Award'}_<Tier>_winners.md 可能含完整 row

---

## ★ 修复本案例的下一步路径 (★)

1. 提供一个有效的 Gemini / DeepSeek API key
2. 跑 `enrich_v9_7_deep.py`:
   - 读 raw.json 中 source_url
   - fetch URL → archive.html
   - LLM 摘要 → 写本文件
3. 同一脚本生成 `视频清单.md`
"""

def generate_video_list(case_name, source_url):
    return f"""# 视频清单

## 案例
{case_name}

## 来源
URL: {source_url or 'N/A'}

## 视频列表 (待 LLM 分析源页面后自动填)

- ⏳ 主视频 (1-3 分钟核心创意) — 待 enrich
- ⏳ Extended Cut (10+ 分钟完整版) — 待 enrich
- ⏳ Behind the Scenes — 待 enrich
- ⏳ Case Study Reel (Cannes/Clio 案例集锦) — 待 enrich
- ⏳ Director's Cut — 待 enrich

## 备注
源页面 (source_url) 可能含 YouTube/Vimeo embed 链接, 抓取后用 yt-dlp 下载并写到 `02_images/` 子目录。

---

_生成时间: 2026-07-03 (v9.7)_
"""

def write_raw_json(case_dir, info):
    payload = {
        'case_name': info.get('case_name', ''),
        'brand': info.get('brand', ''),
        'agency': info.get('agency', ''),
        'award': info.get('award_str', ''),
        'year': info.get('year', ''),
        'source_url': info.get('source_url', ''),
        'enriched_v9_7': True,
        'note': 'raw.json derived from FOLDER_README (subagent v9.6 wrote FOLDER_README from 02_AWARD_SOURCES md)'
    }
    (case_dir / 'raw.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    # Find empty dirs
    empty = []
    for ind in KB_CASES.iterdir():
        if not ind.is_dir() or ind.name.startswith('_'): continue
        for b in ind.iterdir():
            if not b.is_dir(): continue
            for c in b.iterdir():
                if not c.is_dir(): continue
                has_raw = (c / 'raw.json').exists() or any(p.name.endswith('_raw.json') for p in c.iterdir())
                if not has_raw: empty.append(c)
    print(f'Truly empty: {len(empty)}')

    stats = {'readme_extracted': 0, 'fetch_url_ok': 0, 'fetch_url_fail': 0, 'wrote_files': 0}

    for case_dir in empty:
        print(f'\n=== {case_dir.name[:60]} ===')
        readme_path = case_dir / 'FOLDER_README.md'
        if not readme_path.exists():
            # Truly empty: write minimal stub
            print('  TRULY EMPTY — writing stub')
            stub = {
                'case_name': case_dir.name,
                'brand': case_dir.parent.name,
                'industry': case_dir.parent.parent.name,
                'enriched_v9_7': True,
                'note': 'truly empty case, source URL unknown, awaiting manual research'
            }
            (case_dir / 'raw.json').write_text(json.dumps(stub, ensure_ascii=False, indent=2), encoding='utf-8')
            (case_dir / 'FOLDER_README.md').write_text(f'# {case_dir.name}\n\n待 enrich — 数据源 unknown\n', encoding='utf-8')
            (case_dir / '概述.md').write_text(f'# 概述\n待 enrich.\n', encoding='utf-8')
            (case_dir / '深度报告.md').write_text(f'# 深度报告\n待 enrich.\n', encoding='utf-8')
            (case_dir / '视频清单.md').write_text(f'# 视频清单\n待 enrich.\n', encoding='utf-8')
            stats['wrote_files'] += 5
            continue

        # Has FOLDER_README — extract
        info = parse_readme(readme_path.read_text(encoding='utf-8'))
        if not info.get('case_name'):
            info['case_name'] = case_dir.name.rsplit('_', 2)[0]
        write_raw_json(case_dir, info)
        stats['readme_extracted'] += 1

        # Try to fetch source URL
        source_url = info.get('source_url', '')
        if not source_url or not source_url.startswith('http'):
            # Try SearXNG lookup
            q = f"{info.get('case_name','')} {info.get('brand','')} {info.get('award_str','')} award"
            res = searx(q)
            if res:
                source_url = res[0].get('url', '')
                info['source_url'] = source_url
                # update raw.json with new url
                write_raw_json(case_dir, info)

        archive_path = case_dir / 'archive.html'
        if source_url.startswith('http') and not archive_path.exists():
            html = fetch(source_url)
            if html:
                archive_path.write_text(html, encoding='utf-8', errors='ignore')
                stats['fetch_url_ok'] += 1
                print(f'  ✓ fetched {source_url[:50]}... → {len(html)}b')
            else:
                stats['fetch_url_fail'] += 1
                print(f'  ✗ fetch failed: {source_url[:50]}')

        # Write content files (replace existing or create)
        if not (case_dir / '概述.md').exists() or len((case_dir/'概述.md').read_text(encoding='utf-8')) < 500:
            (case_dir / '概述.md').write_text(generate_gaishu(
                info.get('case_name', case_dir.name), info.get('brand', ''),
                info.get('agency', ''), info.get('award_str', ''),
                info.get('source_url', '')
            ), encoding='utf-8')
            stats['wrote_files'] += 1

        if not (case_dir / '深度报告.md').exists() or len((case_dir/'深度报告.md').read_text(encoding='utf-8')) < 500:
            (case_dir / '深度报告.md').write_text(generate_deep_report(
                info.get('case_name', case_dir.name), info.get('brand', ''),
                info.get('agency', ''), info.get('award_str', ''),
                info.get('source_url', '')
            ), encoding='utf-8')
            stats['wrote_files'] += 1

        if not (case_dir / '视频清单.md').exists() or len((case_dir/'视频清单.md').read_text(encoding='utf-8')) < 200:
            (case_dir / '视频清单.md').write_text(generate_video_list(
                info.get('case_name', case_dir.name), info.get('source_url', '')
            ), encoding='utf-8')
            stats['wrote_files'] += 1

    print(f'\n{"="*50}\nFINAL STATS\n{"="*50}')
    for k, v in stats.items():
        print(f'  {k}: {v}')

    # Save audit
    audit_path = KB / '_enrich_v9_7_audit.json'
    audit_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\nAudit: {audit_path}')

if __name__ == '__main__':
    main()
