#!/usr/bin/env python3
"""
exemplar_reasoner.py — Exemplar Reverse-Engineering & Linguistic Alchemy Engine
Deconstructs benchmark copy (Sound, Meaning, Human Intuition) and evolves 5 superior alternatives.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.master_linguistic_engine import MasterLinguisticEngine

class ExemplarReasoner:
    """Masterclass Exemplar Reverse-Engineering & Evolution Engine."""

    def __init__(self, db_path: Optional[Path] = None):
        self.engine = MasterLinguisticEngine()

    def audit_phonetic_cadence(self, text: str) -> Dict[str, Any]:
        """Analyze Chinese phonetic rhythm, syllable symmetry, rhyme flow, and breath gaps."""
        return self.engine.phonetic_analyzer.analyze(text)

    def deconstruct_exemplar(
        self,
        exemplar_copy: str,
        target_audience: str = "目标受众",
        audience_type: str = "default"
    ) -> Dict[str, Any]:
        """Deeply reverse-engineer WHY the exemplar copy works across 3 dimensions."""
        return self.engine.deep_reverse_engineer(exemplar_copy)

    def evolve_beyond_exemplar(
        self,
        exemplar_copy: str,
        brand: str,
        product: str,
        target_audience: str,
        audience_type: str = "default"
    ) -> Dict[str, Any]:
        """Evolve 5 superior slogan archetypes that surpass the exemplar across sound, meaning & intuition."""
        res = self.engine.evolve_master_slogans(
            reference_text=exemplar_copy,
            brand=brand,
            product=product,
            target_audience=target_audience,
            audience_type=audience_type
        )
        
        # Format compatible with previous schema
        evolutions = []
        for ev in res["evolved_slogans"]:
            evolutions.append({
                "archetype": ev["archetype"],
                "tagline": ev["headline"],
                "cadence_eval": ev["cadence_detail"],
                "why_better": ev["why_masterclass"],
                "similarity_benchmark": {
                    "dimension": ev["similarity_benchmark"]["similarity_dimension"],
                    "matched_classic": ev["similarity_benchmark"]["benchmark_case"],
                    "rationale": ev["similarity_benchmark"]["similarity_analysis"]
                }
            })

        return {
            "brand": brand,
            "product": product,
            "target_audience": target_audience,
            "audience_type": audience_type,
            "deconstruction": {
                "exemplar_copy": exemplar_copy,
                "tension_mechanism": res["deconstruction"]["semantic_dimension"]["tension_type"],
                "linguistic_lever": res["deconstruction"]["phonetic_dimension"]["symmetry_description"],
                "sensory_anchor": res["deconstruction"]["intuition_dimension"]["sensory_description"],
                "cadence_analysis": res["deconstruction"]["phonetic_dimension"],
                "deep_rationale": res["deconstruction"]["core_law_summary"]
            },
            "evolutions": evolutions,
            "raw_masterclass_result": res
        }

    def render_evolution_card(self, result: Dict[str, Any]) -> str:
        """Render markdown card for exemplar reverse-engineering and evolution."""
        if "raw_masterclass_result" in result:
            return self.engine.render_masterclass_card(result["raw_masterclass_result"])
        
        dec = result["deconstruction"]
        cad = dec["cadence_analysis"]
        evol_md = ""
        for i, ev in enumerate(result["evolutions"], 1):
            c_score = ev["cadence_eval"]["cadence_score"]
            evol_md += f"""### 方案 {i} · {ev['archetype']}
> 🎯 **超越级口号**:  
> **`「{ev['tagline']}」`**  
>
> 🎵 **声律评分**: `★ {c_score} / 5.0` (节奏: `{ev['cadence_eval']['rhythm_pattern']}` | {ev['cadence_eval']['breath_flow']})  
> 🚀 **超越示范之处**: {ev['why_better']}  

---
"""

        md = f"""# 🔬 示例文案逆向解构与声韵升维全案

> 📌 **输入示例文案**: *"{dec['exemplar_copy']}"*  
> 🎯 **目标客群**: {result['target_audience']} (圈层: {result['audience_type']}) | 📦 **核心产品**: {result['product']}  
> 🏷️ **服务品牌**: {result['brand']}  

---

## 🧬 一、 示例文案底层密码深度逆向工程
> 💡 **核心戏剧张力**: {dec['tension_mechanism']}  
> 🗡️ **语言修辞杠杆**: {dec['linguistic_lever']}  
> 👁️ **直觉通感物象**: {dec['sensory_anchor']}  
> 🎵 **声韵律剖析**: 节奏配比 `{cad['rhythm_pattern']}` | 声律健康分 `★ {cad['cadence_score']}`  

```text
【深度推理结论】
{dec['deep_rationale']}
```

---

## 🏆 二、 基于底层算法演化的 5 大超越级文案
{evol_md}
"""
        return md


if __name__ == "__main__":
    engine = ExemplarReasoner()
    raw = "白天替体面演戏，夜晚让身体稳住"
    res = engine.evolve_beyond_exemplar(
        exemplar_copy=raw,
        brand="稳健伙伴",
        product="亲密健康防护",
        target_audience="都市青年群体",
        audience_type="gay"
    )
    print(engine.render_evolution_card(res))
