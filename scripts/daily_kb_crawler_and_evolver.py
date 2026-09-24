#!/usr/bin/env python3
"""
daily_kb_crawler_and_evolver.py — Automated Daily Marketing Case Crawler & Knowledge Base Evolver
Driven by MiniMax CLI (mmx-cli).

Workflow:
  1. Multi-vector search across marketing & copywriting domains via `mmx-cli search query`
  2. Parse & extract structured advertising cases & slogans via `mmx-cli text chat`
  3. Quality Gate & Multi-dimensional Audit via CopywritingMasteryAuditor (score >= 75.0)
  4. Ingest qualifying cases, slogans & Blake2b vector chunks into `via54_kb.db`
  5. Distill emerging cadence/cognitive laws via `mmx-cli` and evolve `linguistic_laws_and_cadence.json`
  6. Generate daily evolution report and optionally push Feishu notification card
"""

import sys
import os
import json
import re
import sqlite3
import time
import datetime
import subprocess
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.copywriting_art_auditor import CopywritingMasteryAuditor
from via54_store.embedding import hash_embed, encode_blob, _tokenize

MMX_BIN = os.getenv("MMX_CLI_PATH", "/Users/david/.local/bin/mmx-cli")
DB_PATH = PROJECT_ROOT / "via54_kb.db"
LAWS_PATH = PROJECT_ROOT / "knowledge" / "linguistic_laws_and_cadence.json"
EVOLUTION_DIR = PROJECT_ROOT / "data" / "evolution_records"
LOGS_DIR = PROJECT_ROOT / "logs"

# Search queries for daily harvesting
DEFAULT_SEARCH_QUERIES = [
    "2026 优秀广告文案 标杆案例 品牌主张 Slogan",
    "金投赏 戛纳国际创意节 广告门 数英 获奖案例 文案",
    "年度破圈营销 经典广告语 营销战役 复盘",
    "新中式 东方美学 消费品牌 广告词 金句",
    "大健康 科技消费 户外生活 品牌战略 文案洞察"
]


class MmxClient:
    """Wrapper around MiniMax CLI (mmx-cli)."""

    def __init__(self, bin_path: str = MMX_BIN):
        self.bin_path = bin_path
        if not os.path.exists(self.bin_path):
            alt = "/Users/david/.local/bin/mmx"
            if os.path.exists(alt):
                self.bin_path = alt
            else:
                raise FileNotFoundError(f"MiniMax CLI binary not found at {self.bin_path} or {alt}")

    def search(self, query: str, timeout: int = 45) -> List[Dict[str, Any]]:
        """Search the web via `mmx-cli search query --q <query> --output json`."""
        cmd = [self.bin_path, "search", "query", "--q", query, "--output", "json"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            stdout = res.stdout or ""
            start = stdout.find("{")
            end = stdout.rfind("}")
            if start != -1 and end != -1:
                data = json.loads(stdout[start:end+1])
                return data.get("organic", [])
            return []
        except Exception as e:
            print(f"[MmxClient.search] Error running search for '{query}': {e}", file=sys.stderr)
            return []

    def chat(self, prompt: str, system: Optional[str] = None, model: str = "MiniMax-M3", timeout: int = 120) -> str:
        """Call MiniMax chat completion via `mmx-cli text chat`."""
        cmd = [self.bin_path, "text", "chat", "--model", model, "--max-tokens", "8192", "--output", "json"]
        if system:
            cmd.extend(["--system", system])
        cmd.extend(["--message", prompt])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            stdout = res.stdout or ""
            start = stdout.find("{")
            end = stdout.rfind("}")
            if start != -1 and end != -1:
                data = json.loads(stdout[start:end+1])
                contents = data.get("content", [])
                if contents and isinstance(contents, list):
                    return contents[0].get("text", "")
            # Fallback if text format
            return stdout.strip()
        except Exception as e:
            print(f"[MmxClient.chat] Error in text chat: {e}", file=sys.stderr)
            return ""


class DailyCaseHarvester:
    """Harvests and parses candidate advertising cases using mmx-cli."""

    def __init__(self, mmx: MmxClient):
        self.mmx = mmx

    def harvest(self, queries: List[str] = None, max_per_query: int = 6) -> List[Dict[str, Any]]:
        """Execute searches and extract candidate case objects."""
        queries = queries or DEFAULT_SEARCH_QUERIES
        raw_items = []
        seen_links = set()

        print(f"[*] Starting search harvest across {len(queries)} marketing query vectors...")
        for q in queries:
            print(f"  -> Querying: '{q}'")
            items = self.mmx.search(q)
            for it in items[:max_per_query]:
                link = it.get("link", "")
                if link and link not in seen_links:
                    seen_links.add(link)
                    raw_items.append(it)
            time.sleep(1.0)  # gentle pacing

        print(f"[*] Retrieved {len(raw_items)} unique search snippets. Extracting advertising cases via MiniMax-M3...")
        if not raw_items:
            return []

        # Batch items for LLM extraction
        snippets_text = "\n\n".join([
            f"【案例线索 {i+1}】\n标题: {it.get('title')}\n链接: {it.get('link')}\n内容摘录: {it.get('snippet', '')[:800]}"
            for i, it in enumerate(raw_items[:15])
        ])

        system_prompt = (
            "你是一位资深广告营销策略专家与案例分析总监。"
            "你的任务是从给定的商业与营销线索中，提取出真实的品牌广告案例、Campaign战役以及标志性Slogan文案。"
            "必须严格输出 JSON 数组格式，不要包含任何 markdown 代码块以外的解释。"
            "注意：所有字符串内部严禁出现未转义的英文双引号，文案或书名请统一用《》或「」替代；确保输出是合法且严格闭合的 JSON 数组。"
        )

        user_prompt = f"""请分析以下营销线索，提取出所有具备学习与沉淀价值的广告案例与核心文案：

{snippets_text}

请严格按以下 JSON Schema 数组格式返回（若某项非具体广告案例请剔除）：
[
  {{
    "title": "战役或案例名称",
    "brand": "具体品牌名称",
    "industry": "所属行业（如 原叶茶饮/美妆个护/鞋服运动/消费电子/医药健康/汽车 等）",
    "slogan": "核心Slogan/标志性主干文案（若无明确Slogan请提取其核心精髓口号）",
    "consumer_insight": "核心消费者洞察与观念重构逻辑",
    "key_copy_lines": ["战役中的精警文案1", "代表性文案2"],
    "social_meme_tags": ["社交梗标签1", "标签2"],
    "source_url": "来源链接",
    "published_year": 2026
  }}
]
"""
        response_text = self.mmx.chat(user_prompt, system=system_prompt)
        candidates = self._parse_json_array(response_text)
        print(f"[*] Successfully extracted {len(candidates)} structured advertising case candidates.")
        return candidates

    def _parse_json_array(self, text: str) -> List[Dict[str, Any]]:
        """Robustly extract JSON array from model output with fallback to object-by-object recovery."""
        clean_text = text.strip()
        m = re.search(r"```(?:json)?\s*(\[\s*\{.*\}\s*\])\s*```", clean_text, re.DOTALL)
        if m:
            clean_text = m.group(1).strip()
        else:
            start = clean_text.find("[")
            end = clean_text.rfind("]")
            if start != -1 and end != -1:
                clean_text = clean_text[start:end+1].strip()

        # Try direct parse
        try:
            items = json.loads(clean_text)
            if isinstance(items, list):
                return [it for it in items if isinstance(it, dict) and it.get("slogan")]
        except Exception:
            pass

        # Resilient object-by-object regex recovery
        extracted = []
        # Match single JSON objects
        obj_matches = re.finditer(r"\{[^{}]*(?:\"[^\"]*\"[^{}]*)*\}", text, re.DOTALL)
        for om in obj_matches:
            block = om.group(0).strip()
            try:
                obj = json.loads(block)
                if isinstance(obj, dict) and obj.get("slogan"):
                    extracted.append(obj)
            except Exception:
                try:
                    fixed = re.sub(r"[\x00-\x1f]", " ", block)
                    obj = json.loads(fixed)
                    if isinstance(obj, dict) and obj.get("slogan"):
                        extracted.append(obj)
                except Exception:
                    continue

        if extracted:
            return extracted

        print(f"[Harvester] Could not parse JSON array. Preview: {text[:250]}", file=sys.stderr)
        return []


class QualityAuditorAndIngester:
    """Audits candidates using CopywritingMasteryAuditor and ingests qualifying items."""

    def __init__(self, db_path: Path = DB_PATH, threshold_score: float = 75.0):
        self.db_path = db_path
        self.threshold_score = threshold_score
        self.auditor = CopywritingMasteryAuditor(str(self.db_path))

    def audit_and_ingest(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audit each candidate and write passing cases to SQLite."""
        passed_cases = []
        rejected_cases = []
        golden_quotes = []

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        print(f"[*] Starting 6-dimensional Mastery Audit (Threshold: {self.threshold_score}/100)...")

        for idx, case in enumerate(candidates):
            slogan = case.get("slogan", "").strip()
            brand = case.get("brand", "").strip() or "品牌标杆"
            title = case.get("title", "").strip() or f"{brand} 广告战役"

            if not slogan or len(slogan) < 4:
                continue

            audit_res = self.auditor.audit_copywriting(slogan, brand=brand)
            score = audit_res["composite_mastery_score"]
            level = audit_res["mastery_level"]

            case["audit_score"] = score
            case["audit_level"] = level
            case["audit_detail"] = audit_res

            if score >= self.threshold_score:
                print(f"  [✓ PASS {score:.1f}] {brand} · 《{title}》: “{slogan}” -> {level}")
                passed_cases.append(case)

                # Ingest into creative_cases
                self._ingest_case(cur, case)

                # If score >= 82, also record into golden_quotes_and_stunts
                if score >= 82.0:
                    golden_quotes.append(case)
                    self._ingest_golden_quote(cur, case, audit_res)

                # Ingest concept chunks for RAG
                self._ingest_chunks(cur, case, audit_res)
            else:
                print(f"  [✗ FAIL {score:.1f}] {brand} · 《{title}》: “{slogan}” (< {self.threshold_score})")
                rejected_cases.append(case)

        # Log to ingest_log
        now_str = datetime.datetime.now().isoformat()
        cur.execute("""
            INSERT INTO ingest_log (started_at, ended_at, kind, source_path, inserted, updated, skipped, errors, notes)
            VALUES (?, ?, 'daily_mmx_crawl', 'mmx-cli web search', ?, 0, ?, 0, ?)
        """, (now_str, now_str, len(passed_cases), len(rejected_cases), f"Threshold {self.threshold_score}"))

        conn.commit()
        conn.close()

        return {
            "total_candidates": len(candidates),
            "passed_count": len(passed_cases),
            "rejected_count": len(rejected_cases),
            "golden_count": len(golden_quotes),
            "passed_cases": passed_cases,
            "rejected_cases": rejected_cases
        }

    def _ingest_case(self, cur, case: Dict[str, Any]):
        """Insert or replace case in creative_cases table."""
        source_url = case.get("source_url") or f"mmx_crawl_{hashlib.md5(case['slogan'].encode('utf-8')).hexdigest()[:12]}"
        full_markdown = (
            f"# {case['brand']} · {case['title']}\n\n"
            f"> 🎯 **核心Slogan**: **`「{case['slogan']}」`**\n"
            f"> 📊 **Mastery 审计分**: `{case['audit_score']}` ({case['audit_level']})\n\n"
            f"### 💡 核心洞察与策略\n{case.get('consumer_insight', '暂无详细背景')}\n\n"
            f"### ✍️ 战役代表性文案\n" +
            "\n".join([f"- {line}" for line in case.get("key_copy_lines", [])])
        )

        cur.execute("""
            INSERT INTO creative_cases (
                source, source_url, title, brand, industry, published_year,
                published_date, consumer_insight, campaign_slogan, brand_slogan,
                social_meme_tags, raw_content, full_markdown, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(source_url) DO UPDATE SET
                title=excluded.title,
                campaign_slogan=excluded.campaign_slogan,
                consumer_insight=excluded.consumer_insight,
                full_markdown=excluded.full_markdown,
                updated_at=CURRENT_TIMESTAMP
        """, (
            "mmx_crawl",
            source_url,
            case["title"],
            case["brand"],
            case.get("industry", "综合消费"),
            case.get("published_year", 2026),
            datetime.date.today().isoformat(),
            case.get("consumer_insight", ""),
            case["slogan"],
            case["slogan"],
            json.dumps(case.get("social_meme_tags", []), ensure_ascii=False),
            case["slogan"],
            full_markdown
        ))

    def _ingest_golden_quote(self, cur, case: Dict[str, Any], audit_res: Dict[str, Any]):
        """Insert top scoring quote into golden_quotes_and_stunts."""
        source_url = case.get("source_url") or f"quote_{hashlib.md5(case['slogan'].encode('utf-8')).hexdigest()[:12]}"
        rhetoric = audit_res.get("cognitive_rhetoric_dimension", {}).get("verdict", "反常识认知重构")
        cur.execute("""
            INSERT OR REPLACE INTO golden_quotes_and_stunts (
                quote_type, source_platform, brand, industry, headline_or_quote,
                sub_text, core_insight, rhetorical_device, matched_book_methodology,
                published_year, source_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "商业广告标杆金句",
            "mmx_crawl_verified",
            case["brand"],
            case.get("industry", "综合消费"),
            case["slogan"],
            case["title"],
            case.get("consumer_insight", ""),
            rhetoric,
            audit_res.get("master_book_compliance_dimension", {}).get("dominant_school", "定位理论与超级符号"),
            case.get("published_year", 2026),
            source_url
        ))

    def _ingest_chunks(self, cur, case: Dict[str, Any], audit_res: Dict[str, Any]):
        """Create concept and concept_chunks vector embeddings for RAG retrieval."""
        rel_path = f"daily_crawl/{case['brand']}_{case.get('published_year', 2026)}_{hashlib.md5(case['slogan'].encode('utf-8')).hexdigest()[:8]}.md"
        body_text = (
            f"品牌: {case['brand']}\n"
            f"案例: {case['title']}\n"
            f"口号文案: {case['slogan']}\n"
            f"行业: {case.get('industry', '')}\n"
            f"洞察逻辑: {case.get('consumer_insight', '')}\n"
            f"声律平仄: {audit_res.get('phonetic_dimension', {}).get('verdict', '')}\n"
            f"心理语言激活: {audit_res.get('psycholinguistic_activation_dimension', {}).get('dominant_pattern', '')}\n"
        )
        body_hash = hashlib.sha256(body_text.encode("utf-8")).hexdigest()

        now_iso = datetime.datetime.now().isoformat()
        cur.execute("""
            INSERT INTO concepts (
                bundle_id, rel_path, type, title, description, resource, tags_json,
                timestamp, source_path, mtime, body_size, body_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(bundle_id, rel_path) DO UPDATE SET
                title=excluded.title,
                description=excluded.description,
                timestamp=excluded.timestamp,
                body_size=excluded.body_size,
                body_hash=excluded.body_hash
        """, (
            1,  # bundle_id 1
            rel_path,
            "advertising_case",
            f"{case['brand']} · {case['title']}",
            case["slogan"],
            case.get("source_url", ""),
            json.dumps(["广告标杆", case['brand'], case.get('industry', ''), "mmx_crawl"], ensure_ascii=False),
            now_iso,
            "mmx_crawler",
            time.time(),
            len(body_text.encode("utf-8")),
            body_hash
        ))
        cur.execute("SELECT concept_id FROM concepts WHERE bundle_id=? AND rel_path=?", (1, rel_path))
        concept_id = cur.fetchone()[0]

        # Insert chunk
        cur.execute("DELETE FROM concept_chunks WHERE concept_id=?", (concept_id,))
        cur.execute("""
            INSERT INTO concept_chunks (concept_id, chunk_idx, text, char_start, char_end, tokens_json)
            VALUES (?, 0, ?, 0, ?, ?)
        """, (concept_id, body_text, len(body_text), json.dumps([], ensure_ascii=False)))
        chunk_id = cur.lastrowid

        # Terms & Vector blob
        tokens = _tokenize(body_text)
        for tok in set(tokens):
            cur.execute("""
                INSERT OR IGNORE INTO chunk_terms (term, chunk_id, tf)
                VALUES (?, ?, 1.0)
            """, (tok[:50], chunk_id))

        vec = hash_embed(body_text, dim=256)
        blob = encode_blob(vec)
        cur.execute("""
            INSERT OR REPLACE INTO chunk_vector_meta (chunk_id, dim, norm, model)
            VALUES (?, 256, 1.0, 'blake2b-hash-256')
        """, (chunk_id,))
        cur.execute("""
            INSERT OR REPLACE INTO chunk_vector_blob (chunk_id, vec, model)
            VALUES (?, ?, 'blake2b-hash-256')
        """, (chunk_id, blob))


class AlgorithmAndKnowledgeEvolver:
    """Uses mmx-cli to evolve knowledge base laws and brand profiles based on newly ingested cases."""

    def __init__(self, mmx: MmxClient, laws_path: Path = LAWS_PATH):
        self.mmx = mmx
        self.laws_path = laws_path

    def evolve(self, passed_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize newly ingested cases into updated cadence rules and knowledge reflections."""
        if not passed_cases:
            print("[*] No new passed cases today to trigger algorithm evolution.")
            return {"evolved": False, "reason": "No high-scoring cases to distill"}

        print(f"[*] Triggering Knowledge & Algorithm Evolution on {len(passed_cases)} high-scoring cases...")

        cases_summary = "\n".join([
            f"- 品牌: {c['brand']} | 案名: {c['title']}\n"
            f"  口号: 「{c['slogan']}」\n"
            f"  声律分: {c['audit_score']} | 洞察: {c.get('consumer_insight', '')}\n"
            f"  平仄/节拍: {c['audit_detail']['phonetic_dimension'].get('meter_pattern', '')}\n"
            for c in passed_cases[:10]
        ])

        system_prompt = (
            "你是一位深谙汉语语言音系学、认知心理学与广告算法进化架构的首席科学家。"
            "请基于当日入库的高分广告案例与声律审计结果，提炼出最新的文案创作方法论法则。"
        )

        user_prompt = f"""以下是今日经严格 6 维 Mastery 审计入库的优秀广告案例：

{cases_summary}

请结合现有知识库的声律公理与认知神经激活法则，提炼并输出：
1. 【新兴声律节拍特征】：发现的最新句式规律（如 4+4, 6+6, 3+5 或新型长短句对撞节奏）与音韵偏好。
2. 【认知张力与受众心理进化】：当下消费者最敏感的心理防线与观念重构公式（如 A≠B, 昼夜身份撕扯, 具身拟真动作）。
3. 【知识库规则升级建议】：建议增加或更新的 1 条最锋利的文案创作算法法则（包含法则名称、公式/模板、实战范例）。

请以严格规范的 JSON 对象格式返回：
{{
  "evolution_theme": "今日进化主题概述",
  "cadence_insights": "声律节拍与韵律新趋势",
  "psychological_insights": "受众心理与认知张力新特征",
  "new_algorithm_rule": {{
    "rule_name": "规则名称",
    "pattern_or_formula": "句式或逻辑公式",
    "description": "理论依据与心理机制",
    "benchmark_example": "代表性标杆范例"
  }}
}}
"""
        response_text = self.mmx.chat(user_prompt, system=system_prompt)
        evolution_data = self._parse_json_object(response_text)

        if not evolution_data:
            print("[!] Failed to parse evolution JSON from mmx-cli, skipping disk write.", file=sys.stderr)
            return {"evolved": False, "raw_response": response_text}

        # Update linguistic_laws_and_cadence.json
        self._update_laws_file(evolution_data)

        # Write daily digest file
        today_str = datetime.date.today().strftime("%Y%m%d")
        report_file = EVOLUTION_DIR / f"daily_evolution_{today_str}.json"
        md_file = EVOLUTION_DIR / f"daily_evolution_{today_str}.md"

        full_record = {
            "date": today_str,
            "timestamp": datetime.datetime.now().isoformat(),
            "new_cases_count": len(passed_cases),
            "evolution_insights": evolution_data,
            "ingested_cases": [
                {
                    "brand": c["brand"],
                    "title": c["title"],
                    "slogan": c["slogan"],
                    "score": c["audit_score"],
                    "level": c["audit_level"]
                }
                for c in passed_cases
            ]
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(full_record, f, ensure_ascii=False, indent=2)

        md_content = self._render_evolution_markdown(full_record)
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        print(f"[✓] Knowledge & Algorithm Evolution successfully saved to {report_file}")
        return {"evolved": True, "record": full_record, "markdown_report": md_content}

    def _update_laws_file(self, evolution_data: Dict[str, Any]):
        """Append or calibrate laws in linguistic_laws_and_cadence.json."""
        try:
            if not self.laws_path.exists():
                return
            with open(self.laws_path, "r", encoding="utf-8") as f:
                laws = json.load(f)

            rule = evolution_data.get("new_algorithm_rule")
            if rule and isinstance(rule, dict) and rule.get("pattern_or_formula"):
                # Add to rhythm_templates or semantic_tension_laws
                rhythm_templates = laws.setdefault("phonetic_laws", {}).setdefault("rhythm_templates", [])
                new_entry = {
                    "pattern": rule.get("pattern_or_formula", "新型演化格"),
                    "description": f"【自动进化】{rule.get('rule_name', '')}: {rule.get('description', '')}",
                    "example": rule.get("benchmark_example", "")
                }
                # Check duplicate
                if not any(t.get("pattern") == new_entry["pattern"] for t in rhythm_templates):
                    rhythm_templates.append(new_entry)

            # Record in evolution_history
            history = laws.setdefault("evolution_history", [])
            history.append({
                "date": datetime.date.today().isoformat(),
                "theme": evolution_data.get("evolution_theme", "每日算法进化"),
                "insights": evolution_data.get("cadence_insights", "")
            })

            with open(self.laws_path, "w", encoding="utf-8") as f:
                json.dump(laws, f, ensure_ascii=False, indent=2)
            print(f"[✓] Successfully updated {self.laws_path} with new cadence rules.")
        except Exception as e:
            print(f"[!] Warning: Error updating laws file: {e}", file=sys.stderr)

    def _render_evolution_markdown(self, record: Dict[str, Any]) -> str:
        """Render markdown summary of daily evolution."""
        ei = record["evolution_insights"]
        rule = ei.get("new_algorithm_rule", {})
        cases = record["ingested_cases"]

        cases_rows = "\n".join([
            f"| **{c['brand']}** | 《{c['title']}》 | `「{c['slogan']}」` | **{c['score']}** | {c['level']} |"
            for c in cases
        ])

        return f"""# 🧠 知识库与创作算法每日进化简报 ({record['date']})

> 📅 **执行时间**: `{record['timestamp']}`  
> 📥 **今日入库优质案例**: **{record['new_cases_count']}** 个  
> 🤖 **驱动引擎**: MiniMax CLI (`mmx-cli` / MiniMax-M3)

---

## 🏆 今日入库高分案例

| 品牌 | 案例战役 | 标志性文案 / Slogan | 综合审计分 | 评级 |
| :--- | :--- | :--- | :--- | :--- |
{cases_rows}

---

## 🔬 算法与语言公理进化成果

### 1. 🎯 今日进化核心命题: **{ei.get('evolution_theme', '商业语言演化')}**

- 🎵 **声律与节奏新洞察**:
  > {ei.get('cadence_insights', '暂无详细声律变迁')}

- 💡 **受众心智与认知张力**:
  > {ei.get('psychological_insights', '暂无心智张力总结')}

---

### 2. ⚡ 新增/固化创作算法法则

- 📌 **法则名称**: **`{rule.get('rule_name', '新型创作公理')}`**
- 📐 **节奏/公式**: `{rule.get('pattern_or_formula', '无')}`
- 💡 **理论与心理机制**: {rule.get('description', '')}
- 🌟 **标杆范例**: **`「{rule.get('benchmark_example', '')}」`**

---
*本简报由 via54ADIdeahub 自动化守护进程自动生成，并已沉淀至本地 SQLite 与向量索引中。*
"""

    def _parse_json_object(self, text: str) -> Dict[str, Any]:
        """Robustly extract JSON object from model output."""
        try:
            m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
            if m:
                return json.loads(m.group(1))
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
        except Exception as e:
            print(f"[Evolver] JSON parse error: {e}\nRaw preview: {text[:200]}", file=sys.stderr)
        return {}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Daily Marketing Case Crawler & Knowledge Base Evolver")
    parser.add_argument("--threshold", type=float, default=75.0, help="Minimum audit score for ingestion (default: 75.0)")
    parser.add_argument("--dry-run", action="store_true", help="Run search & audit without writing to DB")
    parser.add_argument("--query-limit", type=int, default=3, help="Max search queries to run (default: 3)")
    args = parser.parse_args()

    print("=" * 70)
    print("🚀 via54ADIdeahub Daily Knowledge Base Crawler & Evolver (mmx-cli)")
    print(f"⏰ Start Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    mmx = MmxClient()
    harvester = DailyCaseHarvester(mmx)
    auditor_ingester = QualityAuditorAndIngester(DB_PATH, threshold_score=args.threshold)
    evolver = AlgorithmAndKnowledgeEvolver(mmx, LAWS_PATH)

    # 1. Harvest
    queries = DEFAULT_SEARCH_QUERIES[:args.query_limit]
    candidates = harvester.harvest(queries=queries, max_per_query=5)

    if not candidates:
        print("[!] No candidates extracted today. Exiting.")
        return

    # 2. Audit & Ingest
    if args.dry_run:
        print("[*] Dry-run enabled: skipping database writes.")
        return

    audit_summary = auditor_ingester.audit_and_ingest(candidates)
    passed_cases = audit_summary["passed_cases"]

    print(f"\n[*] Audit Completed: {len(candidates)} audited, {len(passed_cases)} passed, {audit_summary['golden_count']} golden.")

    # 3. Evolve
    if passed_cases:
        evolution_result = evolver.evolve(passed_cases)
        if evolution_result.get("evolved"):
            print("\n🎉 Daily Evolution Completed Successfully!")
            print(evolution_result.get("markdown_report", "")[:600] + "...")
    else:
        print("[*] No cases met the threshold today. Algorithm evolution skipped.")

    print("\n✅ All daily tasks finished cleanly.")


if __name__ == "__main__":
    main()
