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


# ── Entry point ───────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")



