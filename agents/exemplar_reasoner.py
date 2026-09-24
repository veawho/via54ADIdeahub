#!/usr/bin/env python3
"""
exemplar_reasoner.py — Exemplar Reverse-Engineering & Linguistic Alchemy Engine (v2.14.0 Unified Upgrade)
Deconstructs benchmark copy across:
  1. 汉语言声律与真实平仄/十三辙 (Phonetics & Shi-San-Zhe)
  2. 认知张力与修辞机智 (Cognitive Tension & Paradox)
  3. 认知神经与心理语言学激活 (Pulvermüller Embodied Simulation & Damasio Somatic Markers)
  4. 27部大师经典著作合规 (Trout Positioning, LF8, Sugarman Slide)
Evolves 5 superior masterclass alternatives with complete audit scores and benchmarks.
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.master_linguistic_engine import MasterLinguisticEngine
from agents.copywriting_art_auditor import CopywritingMasteryAuditor
from agents.psycholinguistic_activator import PsycholinguisticActivator
from agents.brand_profile_manager import BrandProfileManager


class ExemplarReasoner:
    """Masterclass Exemplar Reverse-Engineering & Evolution Engine v2.14."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (PROJECT_ROOT / "via54_kb.db")
        self.engine = MasterLinguisticEngine()
        self.mastery_auditor = CopywritingMasteryAuditor(self.db_path)
        self.psycholinguistic_activator = PsycholinguisticActivator(self.db_path)
        self.brand_manager = BrandProfileManager()

    def deconstruct_exemplar(
        self,
        exemplar_copy: str,
        brand: str = "",
        target_audience: str = "目标受众",
        audience_type: str = "default"
    ) -> Dict[str, Any]:
        """Deeply reverse-engineer WHY the exemplar copy works across 6 dimensions."""
        mastery_res = self.mastery_auditor.audit_copywriting(exemplar_copy, brand=brand)
        psy_res = self.psycholinguistic_activator.audit_full_psycholinguistics(exemplar_copy)
        legacy_3d = self.engine.deep_reverse_engineer(exemplar_copy)

        return {
            "exemplar_copy": exemplar_copy,
            "brand": brand,
            "mastery_audit": mastery_res,
            "psycholinguistic_audit": psy_res,
            "legacy_3d": legacy_3d
        }

    def evolve_beyond_exemplar(
        self,
        exemplar_copy: str,
        brand: str,
        product: str,
        target_audience: str,
        audience_type: str = "default"
    ) -> Dict[str, Any]:
        """Evolve 5 superior slogan archetypes that surpass the exemplar across sound, meaning & neuro-activation."""
        decon = self.deconstruct_exemplar(
            exemplar_copy=exemplar_copy,
            brand=brand,
            target_audience=target_audience,
            audience_type=audience_type
        )

        legacy_res = self.engine.evolve_master_slogans(
            reference_text=exemplar_copy,
            brand=brand,
            product=product,
            target_audience=target_audience,
            audience_type=audience_type
        )

        evolutions = []
        for ev in legacy_res["evolved_slogans"]:
            headline = ev["headline"]
            ev_audit = self.mastery_auditor.audit_copywriting(headline, brand=brand)
            p_sub = ev_audit["phonetic_dimension"]
            psy_sub = ev_audit["psycholinguistic_activation_dimension"]

            evolutions.append({
                "archetype": ev["archetype"],
                "tagline": headline,
                "composite_mastery_score": ev_audit["composite_mastery_score"],
                "mastery_level": ev_audit["mastery_level"],
                "phonetic_eval": f"声律 ★ {p_sub['phonetic_score']} | 仄起平收: {'✅ 符合' if p_sub['is_ze_qi_ping_shou'] else '❌ 需微调'} | 押韵: {p_sub['matched_rhyme']} | 节拍: {p_sub['rhythm_pattern']}",
                "neuro_eval": f"神经激活 ★ {psy_sub['composite_activation_score']} ({psy_sub['activation_tier']}) | 动机: {psy_sub['regulatory_focus']['dominant_focus']}",
                "why_better": ev["why_masterclass"],
                "similarity_benchmark": ev.get("similarity_benchmark", {}),
                "audit_details": ev_audit
            })

        return {
            "exemplar_copy": exemplar_copy,
            "brand": brand,
            "product": product,
            "target_audience": target_audience,
            "audience_type": audience_type,
            "deconstruction": decon,
            "total_evolutions": len(evolutions),
            "evolutions": evolutions
        }

    def render_evolution_card(self, result: Dict[str, Any]) -> str:
        """Render beautiful Feishu markdown card for exemplar reverse-engineering and evolution."""
        ex = result["exemplar_copy"]
        brand = result["brand"] or "品牌方"
        decon = result["deconstruction"]
        m = decon["mastery_audit"]
        p = m["phonetic_dimension"]
        r = m["cognitive_rhetoric_dimension"]
        b = m["master_book_compliance_dimension"]
        psy = decon["psycholinguistic_audit"]
        emb = psy["embodied_simulation"]
        som = psy["somatic_marker"]
        reg = psy["regulatory_focus"]

        evol_md = ""
        for idx, ev in enumerate(result["evolutions"], 1):
            sim = ev.get("similarity_benchmark", {})
            evol_md += f"""### 方案 {idx} · {ev['archetype']}
> 🎯 **大师级超越口号**:  
> **`「{ev['tagline']}」`**  
>
> 📊 **全维艺术总分**: `★ {ev['composite_mastery_score']} / 100` ({ev['mastery_level']})  
> 🎵 **汉语言声律依据**: {ev['phonetic_eval']}  
> 🧠 **认知神经激活依据**: {ev['neuro_eval']}  
> 🔗 **相似性对标维度**: {sim.get('similarity_dimension', '🏛️ 结构相似性')}  
> 📌 **对标经典案例**: *{sim.get('benchmark_case', '')}*  
> 🔍 **对标借鉴解析**: {sim.get('similarity_analysis', '')}  
> 🚀 **超越升维剖析**: {ev['why_better']}  

---
"""

        md = f"""# 🌌 经典文案全维底层规律逆推与神经激活对标升维全案

> 📌 **参考标注文案**: *"{ex}"*  
> 🎯 **目标客群**: {result['target_audience']} (圈层: {result['audience_type']}) | 📦 **核心产品**: {result['product']}  
> 🏷️ **服务品牌**: {brand}  
> 📊 **参考文案全维基准分**: `★ {m['composite_mastery_score']} / 100` ({m['mastery_level']})  

---

## 🧬 一、 经典文案全维逆推解构 (声律、修辞与认知神经机制)

```text
【汉语音系声律 · 平仄声律与十三辙】
• 节拍律动: {p['rhythm_pattern']} ({p['symmetry_type']})
• 仄起平收: {'✅ 完美符合 (上仄尾平)' if p['is_ze_qi_ping_shou'] else '❌ 需微调'} (尾字声调: {'/'.join(p['tail_pingzes'])})
• 十三辙押韵: {p['matched_rhyme']}
• 声律综合得分: ★ {p['phonetic_score']} / 100

【认知张力与观念重构】
• 核心修辞: {', '.join(r['detected_mechanisms']) or '反差对比'}
• 心智穿透: {r['cognitive_verdict']}
• 认知张力得分: ★ {r['cognitive_score']} / 100

【认知神经与心理语言学激活 (Neuro-Activation)】
• 具身神经拟真 (Pulvermüller): ★ {emb['score']} ({emb['verdict']})
• 躯体标记释怀比 (Damasio): ★ {som['score']} ({som['verdict']})
• 动机语境匹配 (Higgins RFT): {reg['dominant_focus']}
• 神经激活综合得分: ★ {psy['composite_activation_score']} / 100 ({psy['activation_tier']})
```

---

## 🏆 二、 基于底层公理演化的 5 大超越级文案 (含四维相似性对标)
{evol_md}
"""
        return md


if __name__ == "__main__":
    reasoner = ExemplarReasoner()
    raw = "白天替体面演戏，夜晚让身体稳住"
    res = reasoner.evolve_beyond_exemplar(
        exemplar_copy=raw,
        brand="珀莱雅",
        product="高浓度早C晚A精华",
        target_audience="高压职场女性",
        audience_type="women"
    )
    print(reasoner.render_evolution_card(res))
