#!/usr/bin/env python3
"""
via54ADIdeahub MCP Server
Wraps the via54ADIdeahub knowledge base (RAG search + advertising case data)
as an MCP (Model Context Protocol) server for TRAE integration.

Tools exposed:
  - search_knowledge_base: TF-IDF RAG search across creative case reports
  - list_advertising_cases: List/filter advertising cases by industry, brand, award
  - get_case_detail: Get full details of a specific case
  - get_kb_stats: Knowledge base overview statistics

Transport: stdio (JSON-RPC 2.0 over stdin/stdout)
"""

import sys
import os
import json
import re
import sqlite3
from pathlib import Path

# Ensure the project root is on sys.path so we can import via54_rag
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.mcpserver import MCPServer

# ── Paths ──────────────────────────────────────────────
KB_CASES_DIR = PROJECT_ROOT / "docs" / "AD_CASES_KB" / "05_CASES" / "By_Industry"
BUNDLE_DIR = PROJECT_ROOT / "via54_kb_okf_bundle"

# ── MCP Server ────────────────────────────────────────
mcp = MCPServer(
    name="via54ADIdeahub",
    title="via54ADIdeahub Knowledge Base",
    description="Advertising & medical communication creative case knowledge base with RAG search",
    version="1.0.0",
)


# ── Tool: search_knowledge_base ───────────────────────
@mcp.tool()
def search_knowledge_base(query: str, top_k: int = 5) -> str:
    """Search the via54ADIdeahub RAG knowledge base (TF-IDF cosine similarity).

    Searches across advertising/medical communication creative case reports,
    including case overviews, deep reports, creative materials, and video lists.

    Args:
        query: Search query (supports Chinese and English, e.g. "医药品牌情感创意" or "Cannes health")
        top_k: Maximum number of results to return (default 5)

    Returns:
        JSON string with search results containing score, title, doc, and text snippet.
    """
    try:
        from via54_rag import search as rag_search
        results = rag_search(query, top_k=top_k)
        if not results:
            return json.dumps({"message": f"No results found for '{query}'", "results": []}, ensure_ascii=False)
        # Clean up results for MCP response
        clean = []
        for r in results:
            clean.append({
                "score": r.get("score", 0),
                "title": r.get("title", ""),
                "doc": r.get("doc", ""),
                "text": r.get("text", "")[:500],
                "source": r.get("source", "local"),
            })
        return json.dumps({"query": query, "count": len(clean), "results": clean}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: list_advertising_cases ──────────────────────
@mcp.tool()
def list_advertising_cases(
    industry: str = "",
    brand: str = "",
    award: str = "",
    keyword: str = "",
    limit: int = 50,
) -> str:
    """List advertising creative cases from the via54ADIdeahub knowledge base.

    Filter by industry, brand, award, or keyword. Cases are organized by
    industry > brand > case_name, with award tiers (Cannes, Clio, Effie, etc.).

    Args:
        industry: Filter by industry (e.g. "Food_Beverage", "Technology", "Beauty_Personal_Care")
        brand: Filter by brand name (e.g. "Apple", "Coca-Cola", "Dove")
        award: Filter by award (e.g. "Cannes", "Clio", "Effie", "OneShow")
        keyword: Search keyword in case names
        limit: Max results (default 50)

    Returns:
        JSON string with matching cases.
    """
    try:
        results = _scan_cases(industry, brand, award, keyword, limit)
        return json.dumps({
            "total": len(results),
            "filters": {"industry": industry, "brand": brand, "award": award, "keyword": keyword},
            "cases": results,
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: get_case_detail ─────────────────────────────
@mcp.tool()
def get_case_detail(industry: str, brand: str, case_name: str) -> str:
    """Get detailed information about a specific advertising case.

    Retrieve full case files including overview, deep report, creative materials,
    and video list from the knowledge base.

    Args:
        industry: Industry category (e.g. "Apparel_Sportswear")
        brand: Brand name (e.g. "Adidas")
        case_name: Case name/path

    Returns:
        JSON string with case file contents.
    """
    try:
        # Try bundle directory first (OKF bundle format)
        case_key = f"{brand}_{case_name}" if not case_name.startswith(brand) else case_name
        case_files = {}

        # Search in bundle subdirectories
        for subdir in ["case_overviews", "case_studies", "creatives", "videos", "folder_readmes"]:
            d = BUNDLE_DIR / subdir
            if d.exists():
                for f in d.iterdir():
                    if case_name.lower() in f.name.lower() or brand.lower() in f.name.lower():
                        try:
                            content = f.read_text(encoding="utf-8", errors="ignore")
                            case_files[f"{subdir}/{f.name}"] = content[:2000]
                        except Exception:
                            pass

        # Also check the AD_CASES_KB directory
        case_path = KB_CASES_DIR / industry / brand / case_name
        if case_path.exists():
            for f in sorted(case_path.iterdir()):
                if f.is_file() and f.suffix == ".md":
                    try:
                        content = f.read_text(encoding="utf-8", errors="ignore")
                        case_files[f.name] = content[:2000]
                    except Exception:
                        pass

        if not case_files:
            return json.dumps({
                "message": f"No files found for industry={industry}, brand={brand}, case={case_name}",
                "checked_paths": [
                    str(BUNDLE_DIR),
                    str(case_path),
                ],
            }, ensure_ascii=False)

        return json.dumps({
            "industry": industry,
            "brand": brand,
            "case_name": case_name,
            "files": case_files,
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: get_kb_stats ────────────────────────────────
@mcp.tool()
def get_kb_stats() -> str:
    """Get overview statistics of the via54ADIdeahub knowledge base.

    Returns total cases, industries, brands, and breakdowns by industry and award.

    Returns:
        JSON string with knowledge base statistics.
    """
    try:
        cases = _scan_cases(limit=1000)
        industries = {}
        brands = {}
        awards = {}

        for c in cases:
            ind = c.get("industry", "Unknown")
            industries[ind] = industries.get(ind, 0) + 1
            br = c.get("brand", "Unknown")
            brands[br] = brands.get(br, 0) + 1
            aw = c.get("award")
            if aw:
                awards[aw] = awards.get(aw, 0) + 1

        # Also check bundle directory
        bundle_cases = []
        for subdir in ["case_overviews"]:
            d = BUNDLE_DIR / subdir
            if d.exists():
                bundle_cases = list(d.iterdir())

        # Check RAG database
        rag_db_path = PROJECT_ROOT / "vector.db"
        kb_db_path = PROJECT_ROOT / "via54_kb.db"

        return json.dumps({
            "total_cases": len(cases),
            "industries": len(industries),
            "brands": len(brands),
            "awards": len(awards),
            "by_industry": dict(sorted(industries.items(), key=lambda x: -x[1])),
            "by_award": dict(sorted(awards.items(), key=lambda x: -x[1])),
            "bundle_case_files": len(bundle_cases),
            "rag_db_exists": rag_db_path.exists(),
            "kb_db_exists": kb_db_path.exists(),
            "project_path": str(PROJECT_ROOT),
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Helper: scan cases ────────────────────────────────
def _scan_cases(
    industry: str = "",
    brand: str = "",
    award: str = "",
    keyword: str = "",
    limit: int = 50,
) -> list:
    """Scan the case directories and return matching cases."""
    cases = []

    # Scan AD_CASES_KB directory if it exists
    if KB_CASES_DIR.exists():
        for ind_dir in sorted(KB_CASES_DIR.iterdir()):
            if not ind_dir.is_dir() or ind_dir.name == "Unknown":
                continue
            if industry and ind_dir.name != industry:
                continue
            for brand_dir in sorted(ind_dir.iterdir()):
                if not brand_dir.is_dir():
                    continue
                if brand and brand.lower() not in brand_dir.name.lower():
                    continue
                for case_dir in sorted(brand_dir.iterdir()):
                    if not case_dir.is_dir():
                        continue
                    case_name = case_dir.name
                    if keyword and keyword.lower() not in case_name.lower():
                        continue

                    case_data = {
                        "industry": ind_dir.name,
                        "brand": brand_dir.name,
                        "case_name": case_name,
                        "path": str(case_dir.relative_to(PROJECT_ROOT)),
                    }

                    # Extract award from case name
                    m = re.search(r"_(Cannes|Clio|Effie|D&AD|OneShow|Webby|LIA)_", case_name)
                    if m:
                        case_data["award"] = m.group(1)
                    if award and case_data.get("award", "").lower() != award.lower():
                        continue

                    # Check for files
                    files = {f.name for f in case_dir.iterdir() if f.is_file()}
                    case_data["files"] = sorted(files)

                    cases.append(case_data)
                    if len(cases) >= limit:
                        return cases

    # Also scan bundle directory for case overviews
    if not cases and BUNDLE_DIR.exists():
        overview_dir = BUNDLE_DIR / "case_overviews"
        if overview_dir.exists():
            for f in sorted(overview_dir.iterdir()):
                if not f.is_file():
                    continue
                name = f.name
                if keyword and keyword.lower() not in name.lower():
                    continue
                parts = name.split("_")
                case_brand = parts[0] if parts else "Unknown"
                if brand and brand.lower() not in case_brand.lower():
                    continue
                cases.append({
                    "industry": "",
                    "brand": case_brand,
                    "case_name": name.replace("_00_案例概述.md", ""),
                    "path": str(f.relative_to(PROJECT_ROOT)),
                    "source": "bundle",
                })
                if len(cases) >= limit:
                    return cases

    return cases


# ── Tool: search_audience_language ────────────────────
@mcp.tool()
def search_audience_language(audience_type: str = "gay", keyword: str = "") -> str:
    """Retrieve subculture language guidelines, authentic vocabulary, tone guidelines, and taboos.

    Args:
        audience_type: Subculture key ('gay', 'genz', 'women', 'patient', 'default')
        keyword: Optional keyword to filter or check in the subculture guidelines

    Returns:
        JSON string containing subculture name, tags, core keywords, and markdown guidelines.
    """
    try:
        from agents.creative_reasoner import CreativeReasoner
        reasoner = CreativeReasoner()
        ctx = reasoner.get_audience_context(audience_type)
        if keyword and keyword not in ctx.get("guidelines_markdown", ""):
            ctx["keyword_match"] = False
            ctx["keyword_note"] = f"Keyword '{keyword}' not explicitly in glossary, refer to subculture tone guidelines."
        elif keyword:
            ctx["keyword_match"] = True

        return json.dumps(ctx, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: reason_creative_strategy ──────────────────────
@mcp.tool()
def reason_creative_strategy(
    brand: str,
    product: str,
    target_audience: str,
    brief_goal: str,
    audience_type: str = "default",
    style_preference: str = "5大差异化全流派",
    version_count: int = 5,
    emotion_check: bool = True,
) -> str:
    """Generate high-impact creative strategies and 5 distinct slogan options using 2024-2026 Chinese benchmark cases and Critic evaluation.

    Args:
        brand: Brand name (e.g. "霸王茶姬", "稳健伙伴", "某医药品牌")
        product: Product description and core features
        target_audience: Target audience profile (e.g. "00后打工人", "都市青年群体", "慢病患者")
        brief_goal: Campaign objective and challenge to overcome
        audience_type: Target subculture ('gay', 'genz', 'women', 'patient', 'default')
        style_preference: Tone & meme style (e.g. "5大差异化全流派", "去班味+嘴替", "新中式")
        version_count: Number of distinct options to output (default 5, up to 5)
        emotion_check: Enable independent Critic review & quality scoring (default True)

    Returns:
        JSON string containing complete creative reasoning, 5 distinct slogan versions with Critic evaluations, and Feishu card markdown.
    """
    try:
        from agents.creative_reasoner import CreativeReasoner
        reasoner = CreativeReasoner()
        strategy = reasoner.generate_creative_strategy(
            brand=brand,
            product=product,
            target_audience=target_audience,
            brief_goal=brief_goal,
            audience_type=audience_type,
            style_preference=style_preference,
            version_count=version_count,
            enable_critic=emotion_check,
        )
        strategy["markdown_card"] = reasoner.render_feishu_card(strategy)
        return json.dumps(strategy, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: polish_and_diagnose_copy ────────────────────
@mcp.tool()
def polish_and_diagnose_copy(
    draft_text: str,
    target_audience: str,
    brand: str = "",
    audience_type: str = "default",
) -> str:
    """Diagnose user draft copy for preachiness, buzzwords, water words, and rewrite in 3 distinct styles.

    Args:
        draft_text: The user's original copy or slogan draft
        target_audience: Target audience description
        brand: Optional brand name
        audience_type: Target subculture ('gay', 'genz', 'women', 'patient', 'silver', 'pet', 'outdoor', 'default')

    Returns:
        JSON string containing diagnostic breakdown, health score, 3 rewritten options, and Feishu card.
    """
    try:
        from agents.copy_polisher import CopyPolisher
        polisher = CopyPolisher()
        result = polisher.polish_copy(
            draft=draft_text,
            target_audience=target_audience,
            brand=brand,
            audience_type=audience_type,
        )
        result["markdown_card"] = polisher.render_polishing_card(result)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: explore_creative_puns ────────────────────────
@mcp.tool()
def explore_creative_puns(
    brand: str,
    product: str,
    core_benefit: str,
    audience_type: str = "default",
) -> str:
    """Generate high-quality double entendres and evaluate cringe risk using conceptual and phonetic pairing.

    Args:
        brand: Brand name
        product: Product description
        core_benefit: Core benefit or message to convey
        audience_type: Target subculture ('gay', 'genz', 'women', 'patient', 'silver', 'pet', 'outdoor', 'default')

    Returns:
        JSON string containing structured pun proposals, phonetic pairs, and benchmark references.
    """
    try:
        from agents.pun_engine import PunEngine
        engine = PunEngine()
        result = engine.generate_pun_concepts(
            brand=brand,
            product=product,
            core_benefit=core_benefit,
            audience_type=audience_type,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: audit_advertising_compliance ─────────────────
@mcp.tool()
def audit_advertising_compliance(
    text: str,
    audience_type: str = "default",
) -> str:
    """Audit copy text against Chinese advertising law absolute terms and subculture taboos.

    Args:
        text: Copy text to audit
        audience_type: Target subculture ('gay', 'genz', 'women', 'patient', 'silver', 'pet', 'outdoor', 'default')

    Returns:
        JSON string containing compliance violations, risk ratings, and suggested replacement terms.
    """
    try:
        from agents.copy_polisher import CopyPolisher
        polisher = CopyPolisher()
        violations = polisher.audit_compliance(text=text, audience_type=audience_type)
        return json.dumps({
            "is_compliant": len(violations) == 0,
            "violations_count": len(violations),
            "violations": violations
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: deconstruct_and_evolve_copy ─────────────────
@mcp.tool()
def deconstruct_and_evolve_copy(
    exemplar_copy: str,
    brand: str,
    product: str,
    target_audience: str,
    audience_type: str = "default",
) -> str:
    """Deeply reverse-engineer WHY an exemplar benchmark copy works (tension, phonetic cadence, intuition) and evolve 5 superior alternatives.

    Args:
        exemplar_copy: The reference or benchmark copy that user likes
        brand: Brand name
        product: Product description and core features
        target_audience: Target audience description
        audience_type: Target subculture ('gay', 'genz', 'women', 'patient', 'silver', 'pet', 'outdoor', 'default')

    Returns:
        JSON string containing 4-dimensional deconstruction, 5 evolved superior alternatives with phonetic scores, and Feishu card markdown.
    """
    try:
        from agents.exemplar_reasoner import ExemplarReasoner
        engine = ExemplarReasoner()
        result = engine.evolve_beyond_exemplar(
            exemplar_copy=exemplar_copy,
            brand=brand,
            product=product,
            target_audience=target_audience,
            audience_type=audience_type,
        )
        result["markdown_card"] = engine.render_evolution_card(result)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: analyze_linguistic_laws ─────────────────────
@mcp.tool()
def analyze_linguistic_laws(
    copy_text: str,
) -> str:
    """Analyze the phonetic cadence, semantic tension, and human intuition mechanisms of any copy (supports Chinese, English, and Bilingual hybrid).

    Args:
        copy_text: The copywriting or slogan to analyze

    Returns:
        JSON string containing 3-dimensional scores (Sound, Meaning, Intuition), acoustic breakdown, and linguistic summary.
    """
    try:
        from agents.master_linguistic_engine import MasterLinguisticEngine
        engine = MasterLinguisticEngine()
        result = engine.deep_reverse_engineer(copy_text)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: manage_brand_profiles ──────────────────────
@mcp.tool()
def manage_brand_profiles(
    action: str = "list",
    brand_id: str = "",
    profile_json: str = "",
) -> str:
    """Manage brand tone of voice profiles, forbidden words, and rhythm preferences.

    Args:
        action: 'list' (list all profiles), 'get' (get profile by brand_id), or 'save' (create/update profile)
        brand_id: Identifier or brand name (e.g. 'apple', 'proya', 'chagee', 'wenjian')
        profile_json: Optional JSON string for saving a new/updated brand profile

    Returns:
        JSON string with brand profile data or list of profiles.
    """
    try:
        from agents.brand_profile_manager import BrandProfileManager
        mgr = BrandProfileManager()
        if action == "list":
            profiles = mgr.list_profiles()
            return json.dumps({"total": len(profiles), "profiles": profiles}, ensure_ascii=False, indent=2)
        elif action == "get":
            if not brand_id:
                return json.dumps({"error": "brand_id is required for 'get' action"}, ensure_ascii=False)
            profile = mgr.get_profile(brand_id)
            return json.dumps(profile, ensure_ascii=False, indent=2)
        elif action == "save":
            if not profile_json:
                return json.dumps({"error": "profile_json is required for 'save' action"}, ensure_ascii=False)
            data = json.loads(profile_json)
            saved_id = mgr.save_profile(data)
            return json.dumps({"status": "success", "saved_brand_id": saved_id}, ensure_ascii=False)
        else:
            return json.dumps({"error": f"Unknown action '{action}'"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: synthesize_cognitive_slogans ────────────────
@mcp.tool()
def synthesize_cognitive_slogans(
    brand: str,
    product: str,
    target_audience: str,
    brief_goal: str,
    audience_type: str = "default",
) -> str:
    """Synthesize high-impact slogans using Eugene Schwartz awareness stage detection, 16 universal cognitive angles, and Ping-Ze cadence reflection.

    Args:
        brand: Brand name (e.g. "仰望", "观夏", "珀莱雅", "某某品牌")
        product: Product description and core features
        target_audience: Target audience profile
        brief_goal: Campaign objective and challenge to overcome
        audience_type: Optional subculture profile ('default', 'genz', 'women', 'patient', 'gay')

    Returns:
        JSON string containing awareness stage detection, synthesized slogans across universal angles, acoustic cadence scores, and self-correction reflection audit.
    """
    try:
        from agents.rhetorical_alchemy_synthesizer import RhetoricalAlchemySynthesizer
        from agents.creative_reasoner import CreativeReasoner
        reasoner = CreativeReasoner()
        benchmarks = reasoner.retrieve_benchmarks(f"{product} {target_audience}", top_k=3)
        synthesizer = RhetoricalAlchemySynthesizer()
        
        stage_info = synthesizer.detect_awareness_stage(brief_goal, target_audience)
        slogans = synthesizer.synthesize_slogans_with_reflection(
            brand=brand,
            product=product,
            target_audience=target_audience,
            brief_goal=brief_goal,
            benchmarks=benchmarks,
            audience_type=audience_type
        )
        return json.dumps({
            "brand": brand,
            "product": product,
            "target_audience": target_audience,
            "brief_goal": brief_goal,
            "detected_awareness_stage": stage_info,
            "slogans": slogans
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: query_copywriting_books ─────────────────────
@mcp.tool()
def query_copywriting_books(keyword: str = "", book_id: str = "") -> str:
    """Query 27 masterclass copywriting, advertising & translation books (e.g. 《定位》, 《小强广告100招》, 《超级符号》, 《聚焦》, 《影响力》, 《文学翻译谈》, 《余光中谈翻译》, 《钱钟书论翻译》).

    Args:
        keyword: Optional search keyword to filter by author, theory, or school (e.g. '特劳特', '林桂枝', '华与华', 'LF8', '修剪刀')
        book_id: Optional exact book identifier (e.g. 'positioning', 'xiaoqiang_100', 'super_sign', 'cashvertising')

    Returns:
        JSON string containing matching books, thinking paradigms, writing methods, classic cases, and algorithmic heuristics.
    """
    try:
        import sqlite3
        db_path = PROJECT_ROOT / "via54_kb.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if book_id:
            cursor.execute("SELECT * FROM copywriting_methodologies WHERE book_id = ?", (book_id,))
        elif keyword:
            like_kw = f"%{keyword}%"
            cursor.execute("""
                SELECT * FROM copywriting_methodologies
                WHERE title LIKE ? OR author LIKE ? OR school LIKE ? OR core_theory LIKE ?
            """, (like_kw, like_kw, like_kw, like_kw))
        else:
            cursor.execute("SELECT * FROM copywriting_methodologies")

        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        # Parse JSON fields
        for r in rows:
            for f in ["strategy_framework_json", "writing_methods_json", "classic_golden_cases_json", "algorithmic_heuristics_json"]:
                if f in r and isinstance(r[f], str):
                    try:
                        r[f.replace("_json", "")] = json.loads(r[f])
                    except Exception:
                        pass

        return json.dumps({"total": len(rows), "books": rows}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: query_multi_platform_golden_quotes ──────────
@mcp.tool()
def query_multi_platform_golden_quotes(
    platform: str = "",
    quote_type: str = "",
    keyword: str = ""
) -> str:
    """Query multi-platform golden quotes and stunts across Digitaling, TOPYS, Adquan, Meihua, and SocialBeta/Pangjing.

    Args:
        platform: Filter by platform ('数英网', '顶尖文案', '广告门', '梅花网', '胖鲸')
        quote_type: Filter by type ('文案金句', '活动主题金句', '品牌传播主题金句', '事件营销案例', '广告创意案例')
        keyword: Optional search keyword in headline, brand, or core insight

    Returns:
        JSON string containing matched golden quotes, campaigns, book methodology annotations, and event stunts.
    """
    try:
        import sqlite3
        db_path = PROJECT_ROOT / "via54_kb.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query_sql = "SELECT * FROM golden_quotes_and_stunts WHERE 1=1"
        params = []

        if platform:
            query_sql += " AND source_platform LIKE ?"
            params.append(f"%{platform}%")
        if quote_type:
            query_sql += " AND quote_type LIKE ?"
            params.append(f"%{quote_type}%")
        if keyword:
            query_sql += " AND (headline_or_quote LIKE ? OR brand LIKE ? OR sub_text LIKE ? OR matched_book_methodology LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        cursor.execute(query_sql, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        return json.dumps({"total": len(rows), "quotes": rows}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: query_divine_translations ───────────────────
@mcp.tool()
def query_divine_translations(
    keyword: str = "",
    category: str = "",
    translator: str = ""
) -> str:
    """Query canonical 'God-tier' bilingual translations and secondary linguistic reconstruction benchmarks.
    Includes famous translations like '心有猛虎，细嗅蔷薇' (余光中), '生如夏花之绚烂，死如秋叶之静美' (郑振铎),
    '浮世三千，吾爱有三' (古风重构), '相聚有时，后会无期' (后会无期), '与你年轻的时候相比，我更爱你现在备受摧残的面容' (王道乾) etc.

    Args:
        keyword: Search keyword in translation, original text, mechanism, or copywriting insight
        category: Filter by category ('现代诗歌', '文学经典', '爱情神译', '电影台词', '思想箴言')
        translator: Filter by translator name ('余光中', '郑振铎', '王道乾', '杨绛', '王佐良', '许渊冲', '朱生豪', '周克希' etc.)

    Returns:
        JSON string containing matching divine translations with bilingual texts, mechanisms, and copywriting insights.
    """
    try:
        import sqlite3
        db_path = PROJECT_ROOT / "via54_kb.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query_sql = "SELECT * FROM divine_translations WHERE 1=1"
        params = []
        if category:
            query_sql += " AND category LIKE ?"
            params.append(f"%{category}%")
        if translator:
            query_sql += " AND translator LIKE ?"
            params.append(f"%{translator}%")
        if keyword:
            query_sql += " AND (divine_translation LIKE ? OR original_text LIKE ? OR reconstruction_mechanism LIKE ? OR copywriting_insight LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        query_sql += " ORDER BY id ASC"
        cursor.execute(query_sql, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        return json.dumps({"total": len(rows), "translations": rows}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: query_classical_chinese_poetry ──────────────
@mcp.tool()
def query_classical_chinese_poetry(
    keyword: str = "",
    author: str = "",
    dynasty: str = "",
    theme: str = ""
) -> str:
    """Query canonical Classical Chinese Poetry and Prose Masterpieces (中国古典诗词与千古名篇库).
    Includes full texts, golden lines, rhetorical mechanisms, and modern brand copywriting applications
    (e.g., 苏轼《定风波》《赤壁赋》, 李白《将进酒》, 庄子《逍遥游》, 陶渊明《饮酒》, 辛弃疾《青玉案》, 王羲之《兰亭集序》, 范仲淹《岳阳楼记》, 张岱《湖心亭看雪》).

    Args:
        keyword: Search keyword in title, golden lines, full text, or copywriting application
        author: Filter by author (e.g., '苏轼', '李白', '庄子', '陶渊明', '辛弃疾', '王羲之')
        dynasty: Filter by dynasty (e.g., '唐代', '宋代', '先秦', '魏晋', '明清')
        theme: Filter by emotional archetype (e.g., '豁达超脱', '宇宙意识', '极致自信', '极简孤雅', '家国大任')

    Returns:
        JSON string containing matching classical masterpieces with full texts, rhetorical analyses, and copywriting application passwords.
    """
    try:
        import sqlite3
        db_path = PROJECT_ROOT / "via54_kb.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query_sql = "SELECT * FROM classical_chinese_masterpieces WHERE 1=1"
        params = []
        if author:
            query_sql += " AND author LIKE ?"
            params.append(f"%{author}%")
        if dynasty:
            query_sql += " AND dynasty LIKE ?"
            params.append(f"%{dynasty}%")
        if theme:
            query_sql += " AND emotional_archetype LIKE ?"
            params.append(f"%{theme}%")
        if keyword:
            query_sql += " AND (title LIKE ? OR golden_lines LIKE ? OR full_text LIKE ? OR copywriting_application LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        query_sql += " ORDER BY id ASC"
        cursor.execute(query_sql, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        return json.dumps({"total": len(rows), "masterpieces": rows}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: query_oscar_wilde_epigrams ──────────────────
@mcp.tool()
def query_oscar_wilde_epigrams(
    keyword: str = "",
    work: str = "",
    theme: str = ""
) -> str:
    """Query canonical Oscar Wilde Paradox Epigrams & Works (奥斯卡·王尔德唯美主义与悖论金句库).
    Includes bilingual texts, paradox mechanisms, and modern brand copywriting applications
    (e.g., '爱自己是终身浪漫的开始', '我们都在阴沟里但仍有人仰望星空', '我能抗拒一切除了诱惑', '做你自己因为别人已经有人做了', '摆脱诱惑的唯一方法是向它屈服').

    Args:
        keyword: Search keyword in English quote, Chinese translation, paradox mechanism, or copywriting application
        work: Filter by source work (e.g., '道连·格雷的画像', '温夫人的扇子', '不可儿戏', '理想丈夫', '自深深处')
        theme: Filter by theme (e.g., '悦己与浪漫', '欲望与诱惑', '独立与个性', '艺术与现实', '真实与假面')

    Returns:
        JSON string containing matching Oscar Wilde epigrams with bilingual texts, paradox breakdowns, and copywriting insights.
    """
    try:
        import sqlite3
        db_path = PROJECT_ROOT / "via54_kb.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query_sql = "SELECT * FROM oscar_wilde_corpus WHERE 1=1"
        params = []
        if work:
            query_sql += " AND work LIKE ?"
            params.append(f"%{work}%")
        if theme:
            query_sql += " AND theme LIKE ?"
            params.append(f"%{theme}%")
        if keyword:
            query_sql += " AND (chinese_translation LIKE ? OR english_quote LIKE ? OR paradox_mechanism LIKE ? OR copywriting_application LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        query_sql += " ORDER BY id ASC"
        cursor.execute(query_sql, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        return json.dumps({"total": len(rows), "epigrams": rows}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: query_classical_chinese_fulltext ────────────
@mcp.tool()
def query_classical_chinese_fulltext(
    keyword: str = "",
    genre: str = "",
    dynasty: str = "",
    author: str = "",
    limit: int = 20
) -> str:
    """Query full texts of Classical Chinese literature across all major genres (诗经、楚辞、赋、唐诗、宋词、元曲、历代名散文).
    Contains complete unabridged masterworks, historical backgrounds, and aesthetic rhythmic features.

    Args:
        keyword: Search keyword in title, author, full text, or annotations
        genre: Filter by genre ('诗经', '楚辞', '赋', '唐诗', '宋词', '元曲', '散文')
        dynasty: Filter by dynasty ('先秦', '汉代', '三国·魏', '晋代', '唐代', '宋代', '元代', '明代', '清代')
        author: Filter by author name (e.g. '屈原', '李白', '杜甫', '苏轼', '辛弃疾', '李清照', '关汉卿', '王羲之', '陶渊明', '范仲淹', '张岱')
        limit: Max results (default 20)

    Returns:
        JSON string with matching classical Chinese full texts and background analyses.
    """
    try:
        import sqlite3
        db_path = PROJECT_ROOT / "via54_kb.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query_sql = "SELECT * FROM classical_chinese_fulltext WHERE 1=1"
        params = []
        if genre:
            query_sql += " AND genre LIKE ?"
            params.append(f"%{genre}%")
        if dynasty:
            query_sql += " AND dynasty LIKE ?"
            params.append(f"%{dynasty}%")
        if author:
            query_sql += " AND author LIKE ?"
            params.append(f"%{author}%")
        if keyword:
            query_sql += " AND (title LIKE ? OR full_text LIKE ? OR background_and_annotation LIKE ? OR aesthetic_features LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        query_sql += " ORDER BY id ASC LIMIT ?"
        params.append(limit)

        cursor.execute(query_sql, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        return json.dumps({"total": len(rows), "fulltexts": rows}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: query_classical_chinese_golden_quotes ───────
@mcp.tool()
def query_classical_chinese_golden_quotes(
    keyword: str = "",
    emotional_archetype: str = "",
    genre: str = "",
    dynasty: str = "",
    limit: int = 30
) -> str:
    """Query extracted canonical golden quotes from Classical Chinese literature with rhetorical mechanisms and modern brand copywriting directives.
    Linked to original full texts, with deep breakdowns of 赋比兴, 虚实, 互文, 白描, 气象, 通感 and copywriting applications.

    Args:
        keyword: Search keyword in quote text, work title, rhetoric mechanism, or copywriting application
        emotional_archetype: Filter by emotional archetype (e.g. '豁达豪迈', '旷达圆满', '知己共情', '纯爱追求', '家国深情', '极简孤雅', '破局逆袭')
        genre: Filter by genre ('诗经', '楚辞', '赋', '唐诗', '宋词', '元曲', '散文')
        dynasty: Filter by dynasty ('先秦', '三国·魏', '晋代', '唐代', '宋代', '元代', '明代', '明末清初')
        limit: Max results (default 30)

    Returns:
        JSON string with matching classical golden quotes, rhetoric analyses, and copywriting directives.
    """
    try:
        import sqlite3
        db_path = PROJECT_ROOT / "via54_kb.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query_sql = "SELECT * FROM classical_chinese_golden_quotes WHERE 1=1"
        params = []
        if emotional_archetype:
            query_sql += " AND emotional_archetype LIKE ?"
            params.append(f"%{emotional_archetype}%")
        if genre:
            query_sql += " AND genre LIKE ?"
            params.append(f"%{genre}%")
        if dynasty:
            query_sql += " AND dynasty LIKE ?"
            params.append(f"%{dynasty}%")
        if keyword:
            query_sql += " AND (quote_text LIKE ? OR work_title LIKE ? OR author LIKE ? OR rhetorical_mechanisms LIKE ? OR copywriting_application LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        query_sql += " ORDER BY id ASC LIMIT ?"
        params.append(limit)

        cursor.execute(query_sql, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        return json.dumps({"total": len(rows), "golden_quotes": rows}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: query_master_writers_originals ──────────────
@mcp.tool()
def query_master_writers_originals(
    writer: str = "",
    work: str = "",
    keyword: str = "",
    language: str = "",
    limit: int = 20
) -> str:
    """Query Master Writers Originals database (外文原作原本库).
    Contains original foreign texts, chapter excerpts, themes, and literary philosophy across global master writers
    (Oscar Wilde, Shakespeare, Duras, Fitzgerald, Hemingway, Camus, Maugham, Zweig, Borges, Tagore, Kafka).

    Args:
        writer: Filter by writer name in English or Chinese (e.g. 'Oscar Wilde', '王尔德', 'Shakespeare', '莎士比亚', 'Duras', '杜拉斯', 'Camus', '加缪')
        work: Filter by work title in English or Chinese (e.g. 'The Picture of Dorian Gray', '道连·格雷的画像', 'Hamlet', '哈姆雷特', 'L\'Amant', '情人')
        keyword: Search keyword in original text or philosophy
        language: Filter by source language ('English', 'French', 'German', 'Spanish', 'Bengali/English')
        limit: Max results (default 20)

    Returns:
        JSON string containing original foreign texts, context, and philosophical themes.
    """
    try:
        import sqlite3
        db_path = PROJECT_ROOT / "via54_kb.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query_sql = "SELECT * FROM master_writers_originals WHERE 1=1"
        params = []
        if writer:
            query_sql += " AND (writer_name_en LIKE ? OR writer_name_cn LIKE ?)"
            params.extend([f"%{writer}%", f"%{writer}%"])
        if work:
            query_sql += " AND (work_title_en LIKE ? OR work_title_cn LIKE ?)"
            params.extend([f"%{work}%", f"%{work}%"])
        if language:
            query_sql += " AND source_language LIKE ?"
            params.append(f"%{language}%")
        if keyword:
            query_sql += " AND (original_text_extract LIKE ? OR themes_and_philosophy LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        query_sql += " ORDER BY id ASC LIMIT ?"
        params.append(limit)

        cursor.execute(query_sql, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        return json.dumps({"total": len(rows), "originals": rows}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: query_master_writers_translations ───────────
@mcp.tool()
def query_master_writers_translations(
    translator: str = "",
    work: str = "",
    keyword: str = "",
    limit: int = 20
) -> str:
    """Query Master Writers Translations database (名家翻译译本库).
    Contains canonical Chinese translations by legendary translation masters (朱生豪, 王道乾, 余光中, 巫宁坤, 傅雷, 郑振铎, 周煦良, 舒昌善, 王永年, 叶廷芳, 杜小真, 柳鸣九等),
    along with translation school analyses, stylistic aesthetics, and translator commentaries.

    Args:
        translator: Filter by translator name (e.g. '王道乾', '朱生豪', '余光中', '巫宁坤', '郑振铎', '周煦良', '舒昌善', '叶廷芳', '杜小真')
        work: Filter by work title in Chinese (e.g. '情人', '哈姆雷特', '温夫人的扇子', '了不起的盖茨比', '飞鸟集', '月亮与六便士', '变形记')
        keyword: Search keyword in translation text, style analysis, or translator commentary
        limit: Max results (default 20)

    Returns:
        JSON string containing master translations, style critiques, and translator commentaries.
    """
    try:
        import sqlite3
        db_path = PROJECT_ROOT / "via54_kb.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query_sql = "SELECT * FROM master_writers_translations WHERE 1=1"
        params = []
        if translator:
            query_sql += " AND translator LIKE ?"
            params.append(f"%{translator}%")
        if work:
            query_sql += " AND work_title_cn LIKE ?"
            params.append(f"%{work}%")
        if keyword:
            query_sql += " AND (translation_text LIKE ? OR translation_school_and_style LIKE ? OR translator_commentary LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        query_sql += " ORDER BY id ASC LIMIT ?"
        params.append(limit)

        cursor.execute(query_sql, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        return json.dumps({"total": len(rows), "translations": rows}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: query_master_writers_golden_quotes ──────────
@mcp.tool()
def query_master_writers_golden_quotes(
    writer: str = "",
    theme: str = "",
    keyword: str = "",
    limit: int = 30
) -> str:
    """Query Master Writers Golden Epigrams & Paradox Matrix (大师金句库).
    Contains canonical bilingual quotes, paradox mechanisms, cognitive subversion models,
    theme tags, and modern advertising/brand copywriting application blueprints
    (featuring Oscar Wilde paradoxes, Shakespeare, Duras, Fitzgerald, Hemingway, Camus, Maugham, Zweig, Borges, Tagore, Kafka).

    Args:
        writer: Filter by writer name in Chinese or English (e.g. '王尔德', 'Oscar Wilde', '莎士比亚', '杜拉斯', '海明威', '加缪', '毛姆', '泰戈尔')
        theme: Filter by theme tag (e.g. '悦己与浪漫', '欲望与诱惑', '独立与个性', '理想主义', '硬汉精神', '反容貌焦虑', '流动的盛宴')
        keyword: Search keyword in English quote, Chinese translation, paradox mechanism, or copywriting application
        limit: Max results (default 30)

    Returns:
        JSON string containing matching golden epigrams with bilingual texts, rhetorical breakdown, and actionable brand copywriting directives.
    """
    try:
        import sqlite3
        db_path = PROJECT_ROOT / "via54_kb.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query_sql = "SELECT * FROM master_writers_golden_quotes WHERE 1=1"
        params = []
        if writer:
            query_sql += " AND (writer_name_cn LIKE ? OR writer_name_en LIKE ?)"
            params.extend([f"%{writer}%", f"%{writer}%"])
        if theme:
            query_sql += " AND theme_tags_json LIKE ?"
            params.append(f"%{theme}%")
        if keyword:
            query_sql += " AND (translated_quote_cn LIKE ? OR original_quote_lang LIKE ? OR source_work LIKE ? OR rhetorical_and_paradox_mechanism LIKE ? OR copywriting_application LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        query_sql += " ORDER BY id ASC LIMIT ?"
        params.append(limit)

        cursor.execute(query_sql, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        return json.dumps({"total": len(rows), "epigrams": rows}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: audit_and_optimize_copywriting ──────────────
@mcp.tool()
def audit_and_optimize_copywriting(
    text: str,
    target_brand: str = "",
    target_genre: str = ""
) -> str:
    """Perform comprehensive linguistic, rhythmic, rhetorical, and advertising audit on any copy or slogan.
    Evaluates:
      1. Phonetic Cadence (Ping-Ze tones, Ze-Qi-Ping-Shou rule, 13-Zhe rhymes, breath flow)
      2. Literary Genre Fingerprint (诗经/楚辞/赋/唐诗/宋词/元曲/散文/王尔德/杜拉斯/海明威)
      3. Cognitive Tension & Paradox Subversion (A!=B, Day/Night contrast, micro-sensory triggers)
      4. 27 Classic Advertising Books Compliance (Trout Positioning, LF8 Desires, Sugarman Slide, 4U Laws)
      5. Text Purity & Dehydration (detection and penalization of clichés, water fluff, and Europeanized glue words)
      6. Algorithmic Elevation (generates 3 refined variations: 声律工整格、思想悖论格、古典物象格)

    Args:
        text: Slogan or copywriting to audit
        target_brand: Optional brand name to contextualize the audit
        target_genre: Optional target literary genre (e.g. '宋词', '王尔德', '海明威', '唐诗')

    Returns:
        JSON string containing detailed audit scores, diagnostics, and 3 masterclass algorithmic elevation variants.
    """
    try:
        from agents.copywriting_art_auditor import CopywritingMasteryAuditor
        auditor = CopywritingMasteryAuditor()
        audit_result = auditor.audit_copywriting(text, brand=target_brand, target_genre=target_genre)
        report_md = auditor.render_markdown_report(audit_result)
        audit_result["markdown_report"] = report_md
        return json.dumps(audit_result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: audit_psycholinguistic_activation ───────────
@mcp.tool()
def audit_psycholinguistic_activation(
    text: str,
    target_focus: str = ""
) -> str:
    """Audit the neurological, psycholinguistic, and behavioral activation power of any copywriting or slogan.
    Grounded in 10 landmark neuroscience and psychology papers:
      - 具身神经拟真 (Pulvermüller 2005, González 2006)
      - 躯体标记与腹内侧前额叶直觉决策 (Antonio Damasio 1994)
      - 乔纳·伯杰 SPEACC 语言激活矩阵 (Jonah Berger 2023, Bryan 2011)
      - 语言范畴模型与动词具身层级 (Semin & Fiedler 1988, Packard & Berger 2021)
      - 加工流畅度与押韵即真理 (Alter & Oppenheimer 2009, McGlone 2000)
      - 调节聚焦理论 (E. Tory Higgins 1997)
      - VAD 情绪三维高唤醒生理驱动 (Warriner & Brysbaert 2013)
      - 语音象征与布巴-奇奇跨模态感官通感 (Ramachandran & Hubbard 2001)

    Args:
        text: Slogan or copywriting to analyze
        target_focus: Optional target motivational orientation (e.g. 'promotion', 'prevention')

    Returns:
        JSON string containing embodied simulation scores, somatic marker relief ratios, Berger SPEACC metrics, LCM verb hierarchy, regulatory fit, and neuro-elevations.
    """
    try:
        from agents.psycholinguistic_activator import PsycholinguisticActivator
        activator = PsycholinguisticActivator()
        result = activator.audit_full_psycholinguistics(text, target_focus=target_focus)
        result["markdown_section"] = activator.render_markdown_section(result)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Tool: query_psycholinguistic_canon ────────────────
@mcp.tool()
def query_psycholinguistic_canon(
    school_name: str = "",
    figure_or_author: str = "",
    keyword: str = "",
    limit: int = 5
) -> str:
    """Query the Psycholinguistic & Neurological Activation Canon knowledge base.
    Contains 10 seminal psychology schools, landmark research papers, neural mechanisms,
    algorithmic formulas, and copywriting applications.

    Args:
        school_name: Optional school name filter (e.g. '具身认知', '躯体标记', 'SPEACC', '语言范畴模型', '调节聚焦')
        figure_or_author: Optional researcher name (e.g. 'Damasio', 'Jonah Berger', 'Pulvermüller', 'Higgins', 'Langer')
        keyword: Optional search keyword in mechanism, papers, or application insights
        limit: Max results to return (default 5)

    Returns:
        JSON string with matched psycholinguistic canon entries.
    """
    try:
        conn = sqlite3.connect(str(PROJECT_ROOT / "via54_kb.db"))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query_sql = "SELECT * FROM psycholinguistic_activation_canon WHERE 1=1"
        params = []

        if school_name:
            query_sql += " AND (school_name_cn LIKE ? OR school_name_en LIKE ?)"
            params.extend([f"%{school_name}%", f"%{school_name}%"])
        if figure_or_author:
            query_sql += " AND key_figures LIKE ?"
            params.append(f"%{figure_or_author}%")
        if keyword:
            query_sql += " AND (core_psychological_mechanism LIKE ? OR seminal_papers_and_books LIKE ? OR copywriting_application_insight LIKE ? OR canonical_benchmark_cases LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        query_sql += " ORDER BY id ASC LIMIT ?"
        params.append(limit)

        cursor.execute(query_sql, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        return json.dumps({"total": len(rows), "schools": rows}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Entry point ───────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")








