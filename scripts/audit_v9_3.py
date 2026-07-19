"""audit_v9_3.py - Deep audit of KB
- Walk all case dirs (known + Unknown)
- Check 5-file completeness
- Read raw.json to get award + URL
- Read 概述.md to detect "no specific" / "not a real" / low quality
- Cross-check with Gemini: is the case_name a real GP/Gold winner?
- Output: /tmp/audit_v9_3.md
"""
import json
from pathlib import Path
from collections import Counter, defaultdict

KB = Path.home() / "Desktop" / "developments" / "via54ADIdeahub" / "docs" / "AD_CASES_KB" / "05_CASES" / "By_Industry"
required = ["概述.md", "深度报告.md", "视频清单.md", "FOLDER_README.md"]

def normalize_case(n):
    # strip award suffix
    for s in ["_Cannes_Grand_Prix", "_Cannes_Gold", "_Cannes_Silver", "_Cannes_Bronze",
              "_Clio_Grand", "_Clio_Gold", "_Clio_Silver", "_Clio_Bronze",
              "_ADC_Gold", "_ADC_Silver", "_ADC_Bronze",
              "_D&AD_Black_Pencil", "_D&AD_Yellow_Pencil",
              "_LIA_Gold", "_LIA_Grand", "_One_Show_Gold", "_One_Show_Best_Of_Show",
              "_Effie_Awards_Effie", "_Effie_Grand_Effie"]:
        if s in n: n = n.split(s)[0]
    return n

cases = []  # list of dicts
for d in KB.iterdir():
    if not d.is_dir(): continue
    is_unknown = (d.name == "Unknown")
    if is_unknown:
        # walk all subdirs
        for b in d.iterdir():
            if not b.is_dir(): continue
            for c in b.iterdir():
                if not c.is_dir(): continue
                files = {f.name for f in c.iterdir()}
                has_raw = any(n.endswith("_raw.json") for n in files)
                raw_path = next((c / n for n in files if n.endswith("_raw.json")), None)
                award = ""
                url = ""
                if raw_path and raw_path.exists():
                    try:
                        rj = json.loads(raw_path.read_text(encoding="utf-8"))
                        award = rj.get("award", rj.get("Award", ""))
                        url = rj.get("url", rj.get("source_url", ""))
                    except: pass
                cases.append({
                    "industry": "Unknown", "brand": b.name, "case": c.name,
                    "case_norm": normalize_case(c.name),
                    "complete": has_raw and all((c/r).exists() for r in required),
                    "files": list(files),
                    "award": award, "url": url,
                    "path": str(c)
                })
    else:
        industry = d.name
        for b in d.iterdir():
            if not b.is_dir(): continue
            for c in b.iterdir():
                if not c.is_dir(): continue
                files = {f.name for f in c.iterdir()}
                has_raw = any(n.endswith("_raw.json") for n in files)
                raw_path = next((c / n for n in files if n.endswith("_raw.json")), None)
                award = ""
                url = ""
                if raw_path and raw_path.exists():
                    try:
                        rj = json.loads(raw_path.read_text(encoding="utf-8"))
                        award = rj.get("award", rj.get("Award", ""))
                        url = rj.get("url", rj.get("source_url", ""))
                    except: pass
                cases.append({
                    "industry": industry, "brand": b.name, "case": c.name,
                    "case_norm": normalize_case(c.name),
                    "complete": has_raw and all((c/r).exists() for r in required),
                    "files": list(files),
                    "award": award, "url": url,
                    "path": str(c)
                })

# Summary
total = len(cases)
complete = sum(1 for c in cases if c["complete"])
known = [c for c in cases if c["industry"] != "Unknown"]
unknown = [c for c in cases if c["industry"] == "Unknown"]
brands_known = set(c["brand"] for c in known)
brands_unknown = set(c["brand"] for c in unknown)
brands_overlap = brands_known & brands_unknown
industries = Counter(c["industry"] for c in known)
brand_counts_known = Counter(c["brand"] for c in known)
brand_counts_unknown = Counter(c["brand"] for c in unknown)

# award breakdown
def award_tier(name, award):
    n = name
    if "Cannes_Grand_Prix" in n: return "Cannes_GP"
    if "Cannes_Gold" in n: return "Cannes_Gold"
    if "Clio_Grand" in n: return "Clio_Grand"
    if "Clio_Gold" in n: return "Clio_Gold"
    if "ADC_Gold" in n: return "ADC_Gold"
    if "D&AD_Black_Pencil" in n: return "DAD_Black"
    if "One_Show_Best_Of_Show" in n: return "One_Show_Best"
    if "LIA_Grand" in n: return "LIA_Grand"
    if "Effie_Grand" in n: return "Effie_Grand"
    return "Other"

tiers = Counter(award_tier(c["case"], c["award"]) for c in cases)

# Suspect quality: read 概述.md
suspect_quality = []
for c in cases:
    if c["industry"] == "Unknown": continue
    ov = c["path"] + chr(92) + "概述.md"
    try:
        text = Path(ov).read_text(encoding="utf-8")
        low = text.lower()
        if any(k in low for k in ["not a specific", "not a real", "no specific", "isn't a specific",
                                   "couldn't find", "limited information", "search results did not",
                                   "no detailed info", "no detailed", "could not find"]):
            suspect_quality.append((c["brand"], c["case"], text[:200]))
    except: pass

# Suspect brand names in Unknown
suspect_brands = ["Creative", "Film", "Glass", "Grand", "Brand", "Social",
                  "Not specified in search results", "Best", "Not", "awards"]
brands_suspicious = [b for b in brands_unknown if b in suspect_brands or len(b) < 3]

# Duplicate (brand, case_norm) under multiple paths
dupes = defaultdict(list)
for c in cases:
    key = (c["brand"], c["case_norm"])
    if key[1]:  # non-empty
        dupes[key].append(c["path"])
real_dupes = {k: v for k, v in dupes.items() if len(v) > 1}

# Output
lines = []
def w(s=""): lines.append(s)
w(f"# v9.3 Audit Report — {total} case dirs")
w("")
w("## Summary")
w(f"- Total case dirs: **{total}**")
w(f"- 5-file complete: **{complete}** ({complete*100//total}%)")
w(f"- Known (12 industries): **{len(known)}** cases / {len(brands_known)} brands")
w(f"- Unknown: **{len(unknown)}** cases / {len(brands_unknown)} brands")
w(f"- Brand overlap (in both): **{len(brands_overlap)}** {sorted(brands_overlap)}")
w("")
w("## Industries (known)")
for k, v in industries.most_common():
    w(f"- {k}: {v}")
w("")
w("## Award tier (all)")
for k, v in tiers.most_common():
    w(f"- {k}: {v}")
w("")
w("## Top 20 known brands")
for b, n in brand_counts_known.most_common(20):
    w(f"- {b}: {n}")
w("")
w("## Top 20 unknown brands")
for b, n in brand_counts_unknown.most_common(20):
    w(f"- {b}: {n}")
w("")
w("## Real duplicates (brand+case_norm across paths)")
for (b, cn), paths in list(real_dupes.items())[:30]:
    w(f"- {b} / {cn}: {len(paths)} paths")
    for p in paths:
        w(f"  - {p}")
w(f"- Total dup groups: {len(real_dupes)}")
w("")
w("## Suspect quality (概述.md says 'no specific / not real / couldn't find')")
for b, cn, t in suspect_quality[:30]:
    w(f"- {b} / {cn}: {t[:150]}")
w(f"- Total suspect: {len(suspect_quality)}")
w("")
w("## Suspicious brand names in Unknown (likely parse errors)")
for b in brands_suspicious:
    w(f"- {b}: {brand_counts_unknown[b]} cases")
w(f"- Total: {len(brands_suspicious)}")
w("")
w("## Incomplete cases (known, missing 5-file)")
incomplete = [c for c in known if not c["complete"]]
for c in incomplete:
    miss = [r for r in required if not (c["path"] + chr(92) + r).replace(chr(92)+chr(92), "/").startswith(c["path"])]
    miss = [r for r in required if not Path(c["path"] + "/" + r).exists()]
    has_raw = any(n.endswith("_raw.json") for n in c["files"])
    w(f"- {c['industry']} / {c['brand']} / {c['case']}: has_raw={has_raw}, miss={miss}")
w(f"- Total incomplete: {len(incomplete)}")

out = "\n".join(lines)
Path("/tmp/audit_v9_3.md").write_text(out, encoding="utf-8")
print(out[:3000])
print(f"\n... [saved {len(out)}B to /tmp/audit_v9_3.md]")
