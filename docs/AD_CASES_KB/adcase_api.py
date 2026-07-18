"""v8.9: adcase_api — FastAPI 暴露 KB 50 案例给用户访问
端口: 18900 (避开已有 18789 / 18802 / 18900 约定)
"""
import json
import re
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List

KB = Path.home() / "Desktop" / "developments" / "via54ADIdeahub" / "docs" / "AD_CASES_KB"
CASES = KB / "05_CASES" / "By_Industry"

app = FastAPI(title="via54 AD AdCases API", version="v8.9")
app.add_middleware(CORSMiddleware, allow_origins=["*"])

ASCII = re.compile(r"[^\x00-\x7F]")


def scan_cases():
    """scan 05_CASES/By_Industry/*/*/*"""
    cases = []
    for ind in sorted(CASES.iterdir()):
        if not ind.is_dir() or ind.name == "Unknown":
            continue
        for brand in sorted(ind.iterdir()):
            if not brand.is_dir():
                continue
            for case in sorted(brand.iterdir()):
                if not case.is_dir():
                    continue
                files = {f.name for f in case.iterdir()}
                # 真案例 = 至少含 raw.json + 概述
                overview = case / "概述.md"
                raw = None
                for fn in files:
                    if fn.endswith("_raw.json"):
                        raw = case / fn
                        break
                overview_text = ""
                if overview.exists():
                    overview_text = re.sub(r"^#+\s+", "", overview.read_text(encoding="utf-8", errors="ignore")).strip()
                case_data = {
                    "industry": ind.name,
                    "brand": brand.name,
                    "case_name": case.name,
                    "path": str(case.relative_to(KB)),
                    "has_overview": overview.exists(),
                    "files": sorted(files),
                    "summary_ascii": ASCII.sub("?", overview_text[:200]) if overview_text else "",
                }
                # 抽取 award / subaward / tier from case name
                m = re.search(r"_(Cannes|Clio|Effie|D&AD|OneShow|Webby|LIA)_([A-Za-z &]+?)(?:_|$)", case.name)
                if m:
                    case_data["award"] = m.group(1)
                    case_data["subaward"] = m.group(2)
                m2 = re.search(r"_(Grand Prix|Gold|Silver|Bronze)$", case.name)
                if m2:
                    case_data["tier"] = m2.group(1)
                cases.append(case_data)
    return cases


@app.get("/api/health")
def health():
    return {"ok": True, "ts": datetime.now().isoformat()}


@app.get("/api/stats")
def stats():
    cases = scan_cases()
    ind = {}
    brand = {}
    award = {}
    for c in cases:
        ind[c["industry"]] = ind.get(c["industry"], 0) + 1
        brand[c["brand"]] = brand.get(c["brand"], 0) + 1
        if "award" in c:
            award[c["award"]] = award.get(c["award"], 0) + 1
    return {
        "total_cases": len(cases),
        "industries": len(ind),
        "brands": len(brand),
        "awards": len(award),
        "by_industry": ind,
        "by_brand": brand,
        "by_award": award,
        "version": "v8.9",
    }


@app.get("/api/cases")
def list_cases(
    industry: Optional[str] = None,
    brand: Optional[str] = None,
    award: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = Query(100, le=500),
):
    cases = scan_cases()
    if industry:
        cases = [c for c in cases if c["industry"] == industry]
    if brand:
        cases = [c for c in cases if c["brand"] == brand]
    if award:
        cases = [c for c in cases if c.get("award") == award]
    if q:
        ql = q.lower()
        cases = [c for c in cases if ql in c["case_name"].lower() or ql in c["brand"].lower()]
    return {"total": len(cases), "results": cases[:limit]}


@app.get("/api/cases/{industry}/{brand}/{case_name:path}")
def get_case(industry: str, brand: str, case_name: str):
    case_path = CASES / industry / brand / case_name
    if not case_path.exists():
        raise HTTPException(404, "case not found")
    files_info = []
    for f in sorted(case_path.iterdir()):
        if f.is_file():
            content = ""
            if f.suffix == ".md":
                content = f.read_text(encoding="utf-8", errors="ignore")
            elif f.suffix == ".json":
                content = f.read_text(encoding="utf-8", errors="ignore")
            files_info.append({
                "name": f.name,
                "size": f.stat().st_size,
                "content_preview": ASCII.sub("?", content[:600]) if content else ""
            })
    return {
        "industry": industry,
        "brand": brand,
        "case_name": case_name,
        "files": files_info,
    }


@app.get("/api/industries")
def list_industries():
    cases = scan_cases()
    by_ind = {}
    for c in cases:
        by_ind.setdefault(c["industry"], []).append(c)
    return {
        ind: {
            "count": len(cs),
            "brands": sorted({c["brand"] for c in cs}),
        }
        for ind, cs in by_ind.items()
    }


@app.get("/api/brands")
def list_brands():
    cases = scan_cases()
    by_brand = {}
    for c in cases:
        by_brand.setdefault(c["brand"], []).append(c)
    return {
        b: {
            "count": len(cs),
            "industries": sorted({c["industry"] for c in cs}),
            "cases": [c["case_name"] for c in cs],
        }
        for b, cs in by_brand.items()
    }
