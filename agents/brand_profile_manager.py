#!/usr/bin/env python3
"""
brand_profile_manager.py — Brand Tone Profile & Custom Persona Manager
Manages brand-specific voice, cadence preferences, red lines, and sensory anchors.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class BrandProfileManager:
    """Manages brand tone profiles, forbidden words, and cadence preferences."""

    def __init__(self, profile_dir: Optional[Path] = None):
        self.profile_dir = profile_dir or (PROJECT_ROOT / "knowledge" / "brand_profiles")
        self.profile_dir.mkdir(parents=True, exist_ok=True)

    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all available brand profiles."""
        profiles = []
        for f in sorted(self.profile_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                profiles.append({
                    "brand_id": data.get("brand_id", f.stem),
                    "brand_name": data.get("brand_name", f.stem),
                    "tone_of_voice": data.get("tone_of_voice", ""),
                    "similarity_role_model": data.get("similarity_role_model", "")
                })
            except Exception:
                pass
        return profiles

    def get_profile(self, brand_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific brand profile by ID or brand name."""
        # 1. Try exact file stem
        p_file = self.profile_dir / f"{brand_id}.json"
        if p_file.exists():
            try:
                return json.loads(p_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        
        # 2. Try matching by brand_name in all files
        for f in self.profile_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if brand_id.lower() in data.get("brand_name", "").lower() or brand_id.lower() in data.get("brand_id", "").lower():
                    return data
            except Exception:
                pass

        # 3. Fallback default profile
        return {
            "brand_id": brand_id,
            "brand_name": brand_id,
            "tone_of_voice": "真实深刻、自洽从容、平视共鸣",
            "cadence_preference": "对称律动（4+4/6+6）、平仄起伏、开合口尾音",
            "core_spirit": "直击痛点，提供切实可靠的情感共鸣与行动支撑",
            "forbidden_words": ["假大空套话", "低俗生硬", "生造拗口词"],
            "micro_sensory_anchors": ["具体生活细节", "生理直觉动作", "真实场景"],
            "similarity_role_model": "经典获奖案例库"
        }

    def save_profile(self, profile_data: Dict[str, Any]) -> str:
        """Create or update a brand profile."""
        bid = profile_data.get("brand_id") or profile_data.get("brand_name", "custom_brand")
        bid = "".join(c for c in bid if c.isalnum() or c in "_-").lower()
        if not bid:
            bid = "custom_brand"
        
        profile_data["brand_id"] = bid
        target = self.profile_dir / f"{bid}.json"
        target.write_text(json.dumps(profile_data, ensure_ascii=False, indent=2), encoding="utf-8")
        return bid

if __name__ == "__main__":
    mgr = BrandProfileManager()
    all_p = mgr.list_profiles()
    print(f"Total Brand Profiles: {len(all_p)}")
    for p in all_p:
        print(f"- [{p['brand_id']}] {p['brand_name']} -> {p['tone_of_voice']}")
