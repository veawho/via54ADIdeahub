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
    """Query 18 masterclass copywriting & advertising books (e.g. 《定位》, 《小强广告100招》, 《超级符号》, 《吸金广告》).

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


# ── Entry point ───────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")








