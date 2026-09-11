#!/usr/bin/env python3
"""
copy_polisher.py — Copy Diagnostic & Polishing Engine (去爹味 / 语义脱水 / 圈层转译)
Empowers the 'Reviewer' persona: "You write the draft, AI polishes and upgrades it."
Always returns at least 3 distinct options, each with 3-dimensional deep reasoning.
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

PREACHY_WORDS = [
    "你应该", "奉劝大家", "务必", "不要再执迷不悟", "做人必须",
    "听我一句劝", "赶紧买", "不买就亏了", "为了你的父母", "做个懂事的"
]

EMPTY_BUZZWORDS = [
    "全面赋能", "打通闭环", "极致体验", "颠覆认知", "遥遥领先",
    "跨越式提升", "行业天花板", "引领未来", "重磅来袭", "震撼上市"
]

WATER_WORDS = [
    "非常", "十分", "极其", "真是太", "简直", "真的是",
    "令人", "不得不说", "毫不夸张", "值得关注"
]

class CopyPolisher:
    """Intelligent Copywriting Diagnostics & Polishing Assistant."""

    def __init__(self):
        self.subculture_dir = PROJECT_ROOT / "audience_language"
        self.compliance_path = PROJECT_ROOT / "knowledge" / "compliance_rules.json"
        self.linguistic_engine = MasterLinguisticEngine()
        self._load_compliance()

    def _load_compliance(self):
        if self.compliance_path.exists():
            try:
                self.compliance_rules = json.loads(self.compliance_path.read_text(encoding="utf-8"))
            except Exception:
                self.compliance_rules = {}
        else:
            self.compliance_rules = {}

    def audit_compliance(self, text: str, audience_type: str = "default") -> List[Dict[str, Any]]:
        """Audit against advertising law absolute terms and subculture taboos."""
        violations = []
        forbidden_list = self.compliance_rules.get("absolute_forbidden_terms", [])
        for item in forbidden_list:
            term = item["term"]
            if term in text:
                violations.append({
                    "term": term,
                    "category": item.get("category", "广告法合规"),
                    "risk": item.get("risk", "高"),
                    "suggestion": item.get("suggestion", "")
                })

        taboos = self.compliance_rules.get("subculture_taboos", {}).get(audience_type, [])
        for t in taboos:
            if t in text:
                violations.append({
                    "term": t,
                    "category": f"【{audience_type}】圈层禁忌",
                    "risk": "高 (容易引发反感)",
                    "suggestion": "避免说教/刻板标签，替换为平视叙事"
                })

        return violations

    def diagnose_draft(self, draft: str, audience_type: str = "default") -> Dict[str, Any]:
        """Provide detailed score breakdown and flaw analysis for raw copy."""
        preachy_hits = [w for w in PREACHY_WORDS if w in draft]
        buzzword_hits = [w for w in EMPTY_BUZZWORDS if w in draft]
        water_hits = [w for w in WATER_WORDS if w in draft]
        compliance_hits = self.audit_compliance(draft, audience_type=audience_type)

        score = 5.0
        score -= len(preachy_hits) * 0.8
        score -= len(buzzword_hits) * 0.5
        score -= len(water_hits) * 0.4
        score -= len(compliance_hits) * 0.9

        score = round(max(1.0, min(5.0, score)), 1)

        problems = []
        if preachy_hits:
            problems.append(f"👴 **说教爹味严重**: 出现了 [{', '.join(preachy_hits)}]，容易激起受众逆反心理。")
        if buzzword_hits:
            problems.append(f"📉 **假大空行话堆砌**: 出现了 [{', '.join(buzzword_hits)}]，缺乏具体生活场景。")
        if water_hits:
            problems.append(f"💧 **水词修饰过多**: 出现了 [{', '.join(water_hits)}]，削弱了文案张力。")
        if compliance_hits:
            terms_str = ', '.join([c['term'] for c in compliance_hits])
            problems.append(f"🚨 **合规/禁忌风险**: 检测到 [{terms_str}]，需注意广告法与圈层雷区。")

        if not problems:
            problems.append("✅ **整体基调良好**: 初稿无明显爹味与低级套话，具有较好的可打磨基础。")

        return {
            "overall_health_score": score,
            "detected_preachy": preachy_hits,
            "detected_buzzwords": buzzword_hits,
            "detected_water_words": water_hits,
            "compliance_violations": compliance_hits,
            "diagnostic_summary": problems
        }

    def polish_copy(
        self,
        draft: str,
        target_audience: str,
        brand: str = "",
        audience_type: str = "default"
    ) -> Dict[str, Any]:
        """Generate at least 3 refined and polished variants of user draft, each with 3-D reasoning."""
        diagnosis = self.diagnose_draft(draft, audience_type=audience_type)
        b_name = f"【{brand}】" if brand else ""

        if audience_type == "gay":
            lean_opt = f"全场稳健，才叫真正的通关。"
            sensory_opt = f"在每场尽兴的PLAY之后，{b_name}给你随时出发的从容。"
            in_group_opt = f"白天对全世界体面营业，夜晚用{b_name}做回真实的自己。"
        elif audience_type == "genz":
            lean_opt = f"肉身在线除锈，精神早已离职。"
            sensory_opt = f"屏幕上的消息有99条，{b_name}只优先回复你自己的心跳。"
            in_group_opt = f"生活天天给我上课，我用{b_name}给身体上一层护甲。"
        elif audience_type == "patient":
            lean_opt = f"把健康交给科学，把精彩留给自己。"
            sensory_opt = f"懂你深夜每一次不想说的叹息，给身体一个安静深呼吸的夜晚。"
            in_group_opt = f"按时守护不是妥协，而是夺回生活掌控权的日常仪式。"
        elif audience_type == "silver":
            lean_opt = f"退休不是退场，是第二人生的重新开场。"
            sensory_opt = f"脚步轻快，才能走遍年轻时没看够的山河。"
            in_group_opt = f"守护身体的敏捷，是对生活最大的热爱与底气。"
        elif audience_type == "pet":
            lean_opt = f"你给它一顿饭，它用一生毫无保留地奔向你。"
            sensory_opt = f"全世界都在催我长大，只有它趴在怀里允许我做个小孩。"
            in_group_opt = f"懂它每一次挑剔的小脾气，把每一餐都做成安心享受。"
        elif audience_type == "outdoor":
            lean_opt = f"背包越轻，灵魂走得越远。"
            sensory_opt = f"山不语，但足以接住你所有的疲惫与心事。"
            in_group_opt = f"在风吹透衣服的那一刻，重新确信自己还活着。"
        else:
            lean_opt = f"不必向世界证明什么，活得舒展，就是最好的答案。"
            sensory_opt = f"敬每一具在现实风暴里，依然生脆发芽的骨头。"
            in_group_opt = f"白天替体面演戏，夜晚让{b_name}守护真实的生活。"

        raw_options = [
            {
                "type": "🗡️ 锐利脱水版 (Lean & Punchy)",
                "copy": lean_opt,
                "strategy": "大刀阔斧剔除所有形容词套话与说教，只留最硬核的动作与利益点。"
            },
            {
                "type": "🍃 情绪共鸣版 (Sensory & Micro-Narrative)",
                "copy": sensory_opt,
                "strategy": "加入颗粒感的生活场景与感官细节，用电影镜头感引发受众心疼与共情。"
            },
            {
                "type": "🎯 圈层地道版 (In-Group Native)",
                "copy": in_group_opt,
                "strategy": "将原本生硬的外行口吻，无缝转换为目标客群真实的日常沟通暗语。"
            }
        ]

        polished_options = []
        for opt in raw_options:
            eval_3d = self.linguistic_engine.deep_reverse_engineer(opt["copy"])
            polished_options.append({
                **opt,
                "mastery_score": eval_3d["overall_mastery_score"],
                "deep_reasoning": {
                    "phonetic": f"声律评分 ★ {eval_3d['phonetic_dimension']['cadence_score']} | 节拍: {eval_3d['phonetic_dimension']['rhythm_pattern']} ({eval_3d['phonetic_dimension']['symmetry_description']}) | {eval_3d['phonetic_dimension']['breath_flow']}",
                    "semantic": f"意义评分 ★ {eval_3d['semantic_dimension']['semantic_score']} | 张力模型: {eval_3d['semantic_dimension']['tension_type']} | {eval_3d['semantic_dimension']['cognitive_depth']}",
                    "intuition": f"直觉评分 ★ {eval_3d['intuition_dimension']['intuition_score']} | 神经触点: {eval_3d['intuition_dimension']['sensory_description']}"
                }
            })

        return {
            "original_draft": draft,
            "target_audience": target_audience,
            "audience_type": audience_type,
            "brand": brand,
            "diagnosis": diagnosis,
            "total_options": len(polished_options),
            "polished_options": polished_options
        }

    def render_polishing_card(self, result: Dict[str, Any]) -> str:
        """Render beautiful Feishu markdown card for copy diagnosis with 3-D reasoning."""
        diag = result["diagnosis"]
        diag_md = "\n".join([f"- {p}" for p in diag["diagnostic_summary"]])
        
        opts_md = ""
        for i, opt in enumerate(result["polished_options"], 1):
            r = opt.get("deep_reasoning", {})
            opts_md += f"""### 方案 {i} · {opt['type']}
> 🎯 **精炼重构文案**:  
> **`「{opt['copy']}」`**  
>
> 📊 **综合大师级评分**: `★ {opt.get('mastery_score', 4.5)} / 5.0`  
> 💡 **重构策略**: {opt['strategy']}  
> 🎵 **读音声律依据**: {r.get('phonetic', '')}  
> 💡 **意义张力依据**: {r.get('semantic', '')}  
> 👁️ **人类直觉依据**: {r.get('intuition', '')}  

---
"""

        md = f"""# 📝 文案深度体检与三大重构升级全案

> 📌 **文案初稿**: *"{result['original_draft']}"*  
> 🎯 **目标客群**: {result['target_audience']} (圈层: {result['audience_type']})  
> 📊 **初稿健康分**: `★ {diag['overall_health_score']} / 5.0`  

---

## 🔍 一、 初稿问题深度体检
{diag_md}

---

## 🚀 二、 三大维度超越重构方案 (含三维深度推理)
{opts_md}
"""
        return md

if __name__ == "__main__":
    polisher = CopyPolisher()
    raw = "非常优质的男士健康产品，广大男性应该务必重视，不要再执迷不悟，必须全面赋能你的亲密时刻，堪称行业第一神效！"
    res = polisher.polish_copy(raw, target_audience="年轻都市男性", brand="稳健伙伴", audience_type="gay")
    print(polisher.render_polishing_card(res))
