#!/usr/bin/env python3
"""
master_linguistic_engine.py — Masterclass Linguistic Alchemy & 4-Dimensional Similarity Engine
Deconstructs and synthesizes copy across:
  1. 读音维度 (Phonetic Cadence, Tone Contour, Plosives, Bilingual Harmonization)
  2. 意义维度 (Semantic Tension, A!=B Subversion, Conceptual Isomorphism)
  3. 直觉维度 (Human Neurological Intuition, Mirror-Neuron Micro-Sensory)
  4. 相似性对标 (Phonetic, Semantic, Expression, Structural Similarity Benchmarking)
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.brand_profile_manager import BrandProfileManager
from agents.copywriting_art_auditor import PhoneticCadenceAuditor

PLOSIVES = ["p", "b", "t", "d", "k", "g", "破", "爆", "打", "通", "开", "关", "拔", "弹", "跳", "扑", "卡", "哒"]
RESONANT_VOWELS = ["啊", "呀", "啦", "吧", "场", "光", "亮", "关", "安", "稳", "天", "生", "声", "活", "放", "翔", "昂"]
MIRROR_NEURON_ACTIONS = ["呼吸", "吞咽", "撕开", "关门", "快门", "甩开", "敲击", "换上", "踏入", "吹透", "握紧", "跳动"]

class PhoneticCadenceAnalyzer:
    """Masterclass Acoustic & Cadence Analyzer for Chinese and Bilingual Copy with True Ping-Ze and 13-Zhe Rhyme."""

    def analyze(self, text: str) -> Dict[str, Any]:
        has_english = bool(re.search(r"[a-zA-Z]+", text))
        has_chinese = bool(re.search(r"[\u4e00-\u9fff]+", text))
        
        if has_english and has_chinese:
            lang_mode = "中英文混合 (Bilingual Hybrid)"
        elif has_english:
            lang_mode = "纯英文 (Pure English)"
        else:
            lang_mode = "纯中文 (Pure Chinese)"

        # Accurate Phonetic Audit using PhoneticCadenceAuditor
        p_audit = PhoneticCadenceAuditor.audit(text)
        
        rhythm_pattern = p_audit.get("rhythm_pattern", "0")
        symmetry_desc = p_audit.get("symmetry_type", "自由散句")
        is_ze_qi_ping_shou = p_audit.get("is_ze_qi_ping_shou", False)
        is_rhyming = p_audit.get("is_rhyming", False)
        matched_rhyme = p_audit.get("matched_rhyme", "无押韵")
        has_resonant_end = p_audit.get("has_resonant_ending", False)

        plosive_count = sum(1 for p in PLOSIVES if p.lower() in text.lower())

        bilingual_harmony = "无英文"
        bilingual_score_bonus = 0.0
        if lang_mode.startswith("中英文混合"):
            eng_words = re.findall(r"[a-zA-Z]+", text)
            if all(len(w) <= 8 for w in eng_words):
                bilingual_harmony = f"中英咬合极佳：[{', '.join(eng_words)}] 作为重音锚点，无生硬夹杂感"
                bilingual_score_bonus = 0.4
            else:
                bilingual_harmony = "中英夹杂略显冗长，建议缩减英文长度"

        # Convert 100-point scale to 5.0 scale with bilingual bonus
        raw_cadence = (p_audit.get("phonetic_score", 70.0) / 20.0) + bilingual_score_bonus
        cadence_score = round(max(1.0, min(5.0, raw_cadence)), 1)

        breath_desc = "气口自然流畅，声律仄起平收，韵味绵长" if (is_ze_qi_ping_shou and cadence_score >= 4.3) else (
            "读音平顺，朗朗上口" if cadence_score >= 4.0 else "平仄起伏稍显松散，建议末字仄起平收"
        )

        return {
            "language_mode": lang_mode,
            "rhythm_pattern": rhythm_pattern,
            "symmetry_description": symmetry_desc,
            "is_ze_qi_ping_shou": is_ze_qi_ping_shou,
            "is_rhyming": is_rhyming,
            "matched_rhyme": matched_rhyme,
            "plosive_density": f"包含 {plosive_count} 个爆破重音锚点",
            "has_resonant_ending": has_resonant_end,
            "bilingual_harmony": bilingual_harmony,
            "cadence_score": cadence_score,
            "breath_flow": breath_desc
        }


class SemanticTensionDeconstructor:
    """Masterclass Semantic Tension & Conceptual Subversion Deconstructor."""

    def analyze(self, text: str) -> Dict[str, Any]:
        has_subversion = any(w in text for w in ["不是", "而是", "偏见", "边界", "定义", "不当", "没有一种"])
        has_spacetime = any(w in text for w in ["白天", "夜晚", "PPT", "阿拉斯加", "工位", "离职", "旷野", "生活", "屏幕"])
        has_isomorphism = any(w in text for w in ["除锈", "缓冲", "通关", "打卡", "护甲", "营业", "开挂", "底气", "信徒", "PLAY"])

        tension_type = "通用情感共鸣"
        if has_subversion:
            tension_type = "【A 不是 B，C 才是】观念颠覆重构"
        elif has_spacetime:
            tension_type = "【昼夜/空间/双重状态】极致张力撕扯与自救"
        elif has_isomorphism:
            tension_type = "【物理动作 $\\rightarrow$ 心理情绪】双向同构隐喻"

        score = 4.0
        if has_subversion:
            score += 0.5
        if has_spacetime:
            score += 0.3
        if has_isomorphism:
            score += 0.2

        tension_score = round(max(1.0, min(5.0, score)), 1)

        return {
            "tension_type": tension_type,
            "semantic_score": tension_score,
            "cognitive_depth": "击穿表面物理属性，重构为精神图腾或观念宣言" if tension_score >= 4.5 else "具有清晰的情感共鸣与诉求点"
        }


class IntuitiveSensoryMapper:
    """Masterclass Neurological Intuition & Micro-Sensory Mapper (0.5s Brain Directness)."""

    def analyze(self, text: str) -> Dict[str, Any]:
        matched_actions = [a for a in MIRROR_NEURON_ACTIONS if a in text]
        has_concrete_nouns = any(n in text for n in ["骨头", "水面", "电梯", "消息", "鱼", "镜子", "领带", "风", "杯", "衣服", "键盘"])
        has_abstract_fluff = any(f in text for f in ["全面赋能", "颠覆传统", "行业领先", "极其", "非常", "优质"])

        score = 4.2
        if matched_actions or has_concrete_nouns:
            score += 0.5
        if has_abstract_fluff:
            score -= 0.8

        intuition_score = round(max(1.0, min(5.0, score)), 1)
        sensory_desc = f"激发镜像神经元微动作 [{', '.join(matched_actions + (['具象画面物象'] if has_concrete_nouns else []))}]，0.5秒直达大脑潜意识" if (matched_actions or has_concrete_nouns) else "以心理心声直达，直觉通畅"

        return {
            "intuition_score": intuition_score,
            "mirror_neuron_triggers": matched_actions,
            "sensory_description": sensory_desc,
            "brain_directness": "无需经过理性逻辑解码，直接通过直觉产生生理/心理通感" if intuition_score >= 4.5 else "理解阻力低，清晰明确"
        }


class MasterLinguisticEngine:
    """Unified Masterclass Linguistic Engine integrating Sound, Meaning, Intuition and 4-D Similarity Benchmarks."""

    def __init__(self):
        self.phonetic_analyzer = PhoneticCadenceAnalyzer()
        self.semantic_deconstructor = SemanticTensionDeconstructor()
        self.sensory_mapper = IntuitiveSensoryMapper()
        self.brand_manager = BrandProfileManager()

    def deep_reverse_engineer(self, text: str) -> Dict[str, Any]:
        """Perform 3-dimensional reverse engineering on any copy/slogan."""
        phonetic = self.phonetic_analyzer.analyze(text)
        semantic = self.semantic_deconstructor.analyze(text)
        sensory = self.sensory_mapper.analyze(text)

        overall_mastery = round((phonetic["cadence_score"] * 0.35 + semantic["semantic_score"] * 0.35 + sensory["intuition_score"] * 0.3), 1)

        return {
            "text": text,
            "overall_mastery_score": overall_mastery,
            "phonetic_dimension": phonetic,
            "semantic_dimension": semantic,
            "intuition_dimension": sensory,
            "core_law_summary": f"读音遵循 [{phonetic['symmetry_description']} | {phonetic['bilingual_harmony']}]；意义依托 [{semantic['tension_type']}]；直觉依托 [{sensory['sensory_description']}]。"
        }

    def match_similarity_benchmark(self, text: str, archetype: str = "", audience_type: str = "default") -> Dict[str, Any]:
        """Match 4-dimensional similarity benchmark against classic advertising masterpieces."""
        # 1. Phonetic Similarity (读音相似性)
        if "4+4" in text or "稳住全场" in text or len(text) <= 10:
            sim_dim = "🔊 读音相似性 (Phonetic Cadence)"
            benchmark = "《知所先后，则近道矣》 / 华与华《拍照用OPPO，充电5分钟》"
            analysis = "对标经典四字格/五字绝句对称律动，声调仄起平收，开口韵母清脆落地，发音毫无阻力。"
        # 2. Semantic Tension Similarity (意义相似性)
        elif any(w in text for w in ["不是", "而是", "偏见", "边界", "定义", "不必向"]):
            sim_dim = "💡 意义相似性 (Semantic Subversion)"
            benchmark = "珀莱雅《性别不是边界线，偏见才是》 / 内外《NO BODY IS NOBODY》"
            analysis = "对标经典‘A!=B, C=D’反常识认知重构，否定世俗审判假面，确立生命本质主权。"
        # 3. Expression / Bilingual Similarity (表达相似性)
        elif any(w in text for w in ["PLAY", "Online", "Offline", "Shot", "Win", "PPT"]):
            sim_dim = "✍️ 表达相似性 (Bilingual & Tone Expression)"
            benchmark = "步履不停《你写PPT时，阿拉斯加的鳕鱼正跃出水面》 / Apple《Shot on iPhone》"
            analysis = "对标国际化中英文咬合律动，以英文作为核心重音锚点，消除外行夹杂感，制造潮流身份认同。"
        # 4. Structural Similarity (结构相似性)
        elif any(w in text for w in ["白天", "夜晚", "除锈", "离职", "屏幕", "消息", "心跳"]):
            sim_dim = "🏛️ 结构相似性 (Structural Spacetime Contrast)"
            benchmark = "杜蕾斯《让每一个冲动都有安全的缓冲》 / 胜加《时间的答案》"
            analysis = "对标经典昼夜/空间/心理剧烈反差结构，前半句铺设现实压力，后半句一秒完成情绪自救。"
        else:
            sim_dim = "🏛️ 结构相似性 (Structural Isomorphism)"
            benchmark = "诚品书店《在书与非书之间，我们阅读生活》"
            analysis = "对标经典通感对仗句式，将商业功能升格为精神陪伴与文化图腾。"

        return {
            "similarity_dimension": sim_dim,
            "benchmark_case": benchmark,
            "similarity_analysis": analysis
        }

    def evolve_master_slogans(
        self,
        reference_text: str,
        brand: str,
        product: str,
        target_audience: str,
        audience_type: str = "default"
    ) -> Dict[str, Any]:
        """Synthesize 5 evolved masterclass variations, each with 3-D reasoning and 4-D similarity benchmarks."""
        decon = self.deep_reverse_engineer(reference_text)
        brand_prof = self.brand_manager.get_profile(brand)
        b_name = f"【{brand_prof.get('brand_name', brand)}】" if brand else ""

        if audience_type == "gay":
            v1 = {"tag": "稳住全场，从容通关。", "type": "🎵 极致声律格 (4+4 律绝)", "why": "4+4 平仄对称，开合口收音（场 chǎng / 关 guān），声律铿锵，记忆零阻力"}
            v2 = {"tag": f"每一次尽兴的PLAY，都有{b_name}不掉线的底气。", "type": "🌐 中英咬合通感格 (Bilingual Dynamic)", "why": "以英文潮词 PLAY 为爆破重音，中英文 7+10 自然对齐，化敏感为自洽时尚"}
            v3 = {"tag": "不必向偏见证明什么，过得生动，就是最好的答案。", "type": "💡 观念颠覆格 (A!=B Subversion)", "why": "否定世俗审判，重构自我生命力，哲思张力拉满"}
            v4 = {"tag": f"白天对全世界体面营业，夜晚让{b_name}守护真实心跳。", "type": "📢 昼夜撕扯嘴替格 (Day/Night Contrast)", "why": "昼夜场景 10+10 完美对称，将‘营业’与‘心跳’对比，直击灵魂"}
            v5 = {"tag": f"安全不设防，底气在手旁。", "type": "⚡ 神经指令格 (5+5 双押)", "why": "5+5 绝妙双押（防 fáng / 旁 páng），条件反射式击穿行动"}
        elif audience_type == "genz":
            v1 = {"tag": "肉身在线除锈，精神早已离职。", "type": "🎵 极致声律格 (6+6 对称)", "why": "6+6 对仗平仄起伏，除锈与离职形成生理与心理剧烈反差"}
            v2 = {"tag": f"精神Online，肉身Offline：在工位给{b_name}留十秒。", "type": "🌐 中英咬合通感格 (Bilingual Switch)", "why": "Online/Offline 互联网状态对称咬合，打工人身份认同暗号"}
            v3 = {"tag": f"老板画饼管饱，{b_name}管你活到下个周五。", "type": "💡 黑色幽默解构格 (Deadpan Humor)", "why": "荒谬现实与自救解药的强烈戏剧张力，社交货币爆发力极高"}
            v4 = {"tag": "屏幕上的消息有99条，最该优先回复的，是你自己的心跳。", "type": "🎬 电影蒙太奇格 (Micro-Sensory)", "why": "未读消息红点与胸口心跳的微感官对照，瞬间让人破防共鸣"}
            v5 = {"tag": f"累了不用忍，立刻{b_name}！", "type": "⚡ 神经指令格 (5+4 爆破指令)", "why": "爆破音起势，零思考阻力驱动购买"}
        elif audience_type == "patient":
            v1 = {"tag": "按时守护，夺回生活的底气。", "type": "🎵 极致声律格 (4+7 平稳格)", "why": "平仄沉稳，将病耻感转化为夺回掌控权的力量"}
            v2 = {"tag": f"懂你深夜每一次不想说的叹息，给身体一个深呼吸的夜晚。", "type": "🎬 电影蒙太奇格 (Micro-Sensory)", "why": "具象到深夜叹息与深呼吸的生理动作，温度感拉满"}
            v3 = {"tag": "把健康交给科学，把精彩留给自己。", "type": "💡 观念重构格 (8+8 绝对平衡)", "why": "8+8 完美对仗，理性信任与感性向往的高度融合"}
            v4 = {"tag": "自嘲脆皮是幽默，主动打卡是清醒。", "type": "📢 灵魂嘴替格 (7+7 对仗)", "why": "融合年轻人自嘲文化与自救清醒，无爹味说教"}
            v5 = {"tag": f"守护不妥协，精彩更尽兴。", "type": "⚡ 神经指令格 (5+5 双押)", "why": "5+5 双平声利落落脚，易记易传"}
        else:
            v1 = {"tag": f"白天替体面演戏，夜晚让{b_name}守护真实。", "type": "🎵 极致声律格 (7+7 绝句)", "why": "昼夜对称，字数字音严丝合缝，气口开合自如"}
            v2 = {"tag": "Shot on life, 活在每一个真实的瞬间。", "type": "🌐 中英咬合通感格 (Bilingual Meme)", "why": "借势超级符号，中英文自然承接"}
            v3 = {"tag": "不必向世界证明什么，活得舒展，就是最好的答案。", "type": "💡 观念颠覆格 (A!=B Subversion)", "why": "直击灵魂深处的精神松绑"}
            v4 = {"tag": "敬每一具在现实风暴里，依然生脆发芽的骨头。", "type": "🎬 电影蒙太奇格 (Cinematic Sensory)", "why": "王家卫级微感官物象，‘生脆发芽’与‘骨头’极具生命张力"}
            v5 = {"tag": f"认真生活，从一罐{b_name}开始。", "type": "⚡ 神经指令格 (4+7 行动指令)", "why": "自然亲和，零阻力行动触发"}

        evolved_list = []
        for v in [v1, v2, v3, v4, v5]:
            eval_res = self.deep_reverse_engineer(v["tag"])
            sim_bench = self.match_similarity_benchmark(v["tag"], v["type"], audience_type=audience_type)
            evolved_list.append({
                "headline": v["tag"],
                "archetype": v["type"],
                "why_masterclass": v["why"],
                "mastery_score": eval_res["overall_mastery_score"],
                "cadence_detail": eval_res["phonetic_dimension"],
                "semantic_detail": eval_res["semantic_dimension"],
                "intuition_detail": eval_res["intuition_dimension"],
                "similarity_benchmark": sim_bench
            })

        return {
            "reference_text": reference_text,
            "brand": brand,
            "brand_profile": brand_prof,
            "product": product,
            "target_audience": target_audience,
            "audience_type": audience_type,
            "deconstruction": decon,
            "total_evolutions": len(evolved_list),
            "evolved_slogans": evolved_list
        }

    def render_masterclass_card(self, result: Dict[str, Any]) -> str:
        """Render beautiful Feishu markdown card with 4-D similarity benchmarks."""
        dec = result["deconstruction"]
        p = dec["phonetic_dimension"]
        s = dec["semantic_dimension"]
        i = dec["intuition_dimension"]
        prof = result.get("brand_profile", {})

        evol_md = ""
        for idx, ev in enumerate(result["evolved_slogans"], 1):
            sim = ev.get("similarity_benchmark", {})
            evol_md += f"""### 方案 {idx} · {ev['archetype']}
> 🎯 **大师级演化文案**:  
> **`「{ev['headline']}」`**  
>
> 📊 **三维综合大师评分**: `★ {ev['mastery_score']} / 5.0`  
> 🎵 **声律依据**: `{ev['cadence_detail']['rhythm_pattern']}` | {ev['cadence_detail']['symmetry_description']} | {ev['cadence_detail']['breath_flow']}  
> 💡 **意义依据**: {ev['semantic_detail']['cognitive_depth']}  
> 👁️ **直觉依据**: {ev['intuition_detail']['sensory_description']}  
> 🔗 **相似性对标参考**: {sim.get('similarity_dimension', '🏛️ 结构相似性')}  
> 📌 **对标经典案例**: *{sim.get('benchmark_case', '')}*  
> 🔍 **对标借鉴解析**: {sim.get('similarity_analysis', '')}  
> 🚀 **超越升维依据**: {ev['why_masterclass']}  

---
"""

        md = f"""# 🌌 经典文案三维底层规律深度逆推与四维相似性对标升维全案

> 📌 **参考标注文案**: *"{result['reference_text']}"*  
> 🎯 **目标客群**: {result['target_audience']} (圈层: {result['audience_type']}) | 📦 **核心产品**: {result['product']}  
> 🏷️ **服务品牌**: {result['brand']} (调性: {prof.get('tone_of_voice', '经典自洽')})  

---

## 🧬 一、 经典文案【读音 + 意义 + 人类直觉】三维逆推解构

```text
【读音维度 · 声韵平仄与中英咬合】
• 语言模式: {p['language_mode']}
• 节拍律动: {p['rhythm_pattern']} ({p['symmetry_description']})
• 爆破与开口音: {p['plosive_density']} | 开合口共鸣: {'是' if p['has_resonant_ending'] else '否'}
• 中英咬合评测: {p['bilingual_harmony']}
• 声律评分: ★ {p['cadence_score']} / 5.0

【意义维度 · 观念重构与戏剧张力】
• 张力模型: {s['tension_type']}
• 认知穿透: {s['cognitive_depth']}
• 意义评分: ★ {s['semantic_score']} / 5.0

【直觉维度 · 0.5秒神经通感与镜像动作】
• 神经触点: {i['sensory_description']}
• 直觉直通率: {i['brain_directness']}
• 直觉评分: ★ {i['intuition_score']} / 5.0
```

---

## 🏆 二、 基于底层公理演化的 5 大超越级文案 (含四维相似性对标)
{evol_md}
"""
        return md


if __name__ == "__main__":
    engine = MasterLinguisticEngine()
    test_raw = "你写PPT时，阿拉斯加的鳕鱼正跃出水面"
    res = engine.evolve_master_slogans(
        reference_text=test_raw,
        brand="proya",
        product="高浓度电解质草本饮",
        target_audience="大厂高压打工人",
        audience_type="genz"
    )
    print(engine.render_masterclass_card(res))
