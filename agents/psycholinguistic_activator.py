#!/usr/bin/env python3
"""
psycholinguistic_activator.py — Neurological & Psycholinguistic Activation Engine
Grounded in landmark psycholinguistics, cognitive neuroscience, and behavioral economics papers:
  1. 具身神经拟真 (Pulvermüller 2005, González 2006, Williams & Bargh 2008)
  2. 躯体标记与腹内侧前额叶直觉决策 (Antonio Damasio 1994)
  3. 乔纳·伯杰 SPEACC 语言激活矩阵 (Jonah Berger 2023, Bryan & Walton 2011)
  4. 语言范畴模型与动词具身层级 (Semin & Fiedler 1988, Packard & Berger 2021)
  5. 加工流畅度与押韵即真理 (Alter & Oppenheimer 2009, McGlone 2000)
  6. 调节聚焦理论 (E. Tory Higgins 1997, Aaker & Lee 2001)
  7. VAD 情绪三维高唤醒生理驱动 (Warriner & Brysbaert 2013, Russell 1980)
  8. 语音象征与布巴-奇奇跨模态感官通感 (Ramachandran & Hubbard 2001, Yorkston & Menon 2004)
  9. 心智无意识“因为”启发式 (Ellen Langer 1978, Tversky & Kahneman 1981)
"""

import sys
import os
import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    from pypinyin import pinyin, Style
    HAS_PYPINYIN = True
except ImportError:
    HAS_PYPINYIN = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ── 1. 具身运动与感官物理微词典 (Embodied Somatosensory Lexicon) ──
MOTOR_ACTION_VERBS = [
    "撕", "咬", "踩", "奔", "拔", "握", "跃", "劈", "推", "扣",
    "踏", "抓", "切", "穿", "敲", "拆", "撞", "拽", "掀", "踢", "揽"
]

SENSORY_PHYSICAL_TEXTURES = [
    "温热", "冰凉", "粗糙", "细腻", "酥脆", "醇厚", "微苦", "清冽",
    "刺痛", "滚烫", "回甘", "滑润", "焦香", "清甜", "甘甜", "柔韧", "微甜"
]

# ── 2. 躯体标记生理应激与释怀词典 (Somatic Marker Lexicon) ──
VISCERAL_STRESS_MARKERS = [
    "窒息", "冷汗", "紧绷", "疲惫", "掏空", "锁死", "阵痛", "透支",
    "焦虑", "沉重", "压抑", "内卷", "班味", "慌乱", "失控", "心力交瘁"
]

VISCERAL_RELIEF_MARKERS = [
    "深呼吸", "释怀", "舒展", "回甘", "踏实", "松弛", "卸下", "回血",
    "安放", "治愈", "熨帖", "自洽", "抚平", "轻盈", "苏醒", "透气"
]

# ── 3. 乔纳·伯杰 SPEACC 激活词典 (Berger SPEACC Lexicon) ──
IDENTITY_NOUN_FRAMES = [
    "探索者", "清醒者", "同行人", "破局者", "生活家", "守门人",
    "创造者", "摆渡人", "野心家", "领跑者", "掌舵人", "先行者", "追光者"
]

HIGH_CONFIDENCE_WORDS = [
    "必定", "终将", "彻底", "毫无疑问", "永远", "绝对", "笃定", "确信", "必定会", "必然"
]

HEDGING_TABOO_WORDS = [
    "可能", "也许", "大概", "某种程度上", "试一试", "说不定", "差不多", "基本上"
]

SELF_GENERATION_PROMPTS = [
    "凭什么", "为什么不", "何不", "难道", "谁说", "何必", "岂止", "哪有"
]

# ── 4. 语言范畴模型 (Linguistic Category Model - LCM) ──
LCM_DAVS = MOTOR_ACTION_VERBS + ["涂", "抹", "喝", "吹", "咬", "走", "看", "点", "抱"]
LCM_IAVS = ["守护", "治愈", "打破", "赋能", "重构", "超越", "欺骗", "救赎", "颠覆", "唤醒", "解救"]
LCM_SVS = ["爱", "恨", "渴望", "向往", "留恋", "崇拜", "畏惧", "珍惜", "信赖", "期待"]
LCM_ABSTRACT_ADJS = [
    "卓越", "尊贵", "极致", "非凡", "领先", "完美", "优越", "高端",
    "奢华", "优质", "优秀", "顶尖", "强大", "超凡", "无比"
]

# ── 5. 调节聚焦理论词典 (Regulatory Focus Lexicon) ──
PROMOTION_WORDS = [
    "突破", "解锁", "跃升", "赢得", "渴望", "升级", "无畏", "尽兴",
    "领跑", "追逐", "探索", "盛开", "张扬", "超越", "奔向", "创造"
]

PREVENTION_WORDS = [
    "守住", "底气", "安全", "不负", "踏实", "规避", "兜底", "可靠",
    "防范", "无忧", "守护", "坚守", "定力", "护甲", "托付", "稳固"
]

# ── 6. VAD 情绪高唤醒度词典 (High Arousal Warriner/Russell) ──
HIGH_AROUSAL_WORDS = [
    "震撼", "狂欢", "沸腾", "夺目", "燃烧", "呼啸", "惊艳", "尖叫",
    "爆发", "狂澜", "激荡", "翻涌", "电光火石", "摧枯拉朽", "痛快"
]

HIGH_DOMINANCE_WORDS = [
    "掌控", "主场", "执掌", "自洽", "定义", "从容", "底牌", "说了算", "傲立", "无拘"
]

# ── 7. 因果启发式与损失厌恶词典 ──
CAUSAL_CONNECTORS = ["因为", "正因如此", "之所以", "所以", "才能", "方能", "由此"]
LOSS_AVERSION_PHRASES = ["别让", "别等失去", "少走弯路", "不可逆", "代价", "遗憾", "荒废", "错付"]


class PsycholinguisticActivator:
    """Calculates multidimensional neurological, psycholinguistic, and behavioral activation scores."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (PROJECT_ROOT / "via54_kb.db")

    def audit_embodied_simulation(self, text: str) -> Dict[str, Any]:
        """Pulvermüller & González: Motor cortex & sensory cortex direct neural simulation."""
        motor_hits = [w for w in MOTOR_ACTION_VERBS if w in text]
        sensory_hits = [w for w in SENSORY_PHYSICAL_TEXTURES if w in text]

        raw_score = len(motor_hits) * 35.0 + len(sensory_hits) * 30.0
        # Baseline score: if text has concrete physical nouns, award baseline
        if any(w in text for w in ["手", "脚", "骨", "风", "光", "水", "火", "土", "夜", "晨"]):
            raw_score += 25.0
        score = min(100.0, max(20.0, raw_score))

        return {
            "score": round(score, 1),
            "motor_hits": motor_hits,
            "sensory_hits": sensory_hits,
            "verdict": "🔥 运动与感觉皮层高烈度放电 (强具身拟真)" if score >= 75 else (
                "⚡ 具备基础物理物象，能引发初级联觉" if score >= 50 else "⚠️ 缺乏具象肌肉动词与物理触感，神经激活偏弱"
            )
        }

    def audit_somatic_marker(self, text: str) -> Dict[str, Any]:
        """Antonio Damasio: Visceral tension-relief emotional bookmarking."""
        stress_hits = [w for w in VISCERAL_STRESS_MARKERS if w in text]
        relief_hits = [w for w in VISCERAL_RELIEF_MARKERS if w in text]

        has_tension_release = (len(stress_hits) > 0 and len(relief_hits) > 0)
        score = 88.0 if has_tension_release else (
            76.0 if len(relief_hits) > 0 or len(stress_hits) > 0 else 60.0
        )

        return {
            "score": score,
            "stress_markers": stress_hits,
            "relief_markers": relief_hits,
            "has_tension_release": has_tension_release,
            "verdict": "🎯 完美触发‘生理压迫 $\\rightarrow$ 生理释怀’躯体标记电位差" if has_tension_release else (
                "💡 命中单向生理标记词，具较好共鸣" if (stress_hits or relief_hits) else "⚠️ 未探测到微观躯体生理反应锚点"
            )
        }

    def audit_berger_speacc(self, text: str) -> Dict[str, Any]:
        """Jonah Berger: SPEACC (Similarity, Posing questions, Emotion, Agency, Confidence, Concreteness)."""
        # Identity
        identity_hits = [w for w in IDENTITY_NOUN_FRAMES if w in text]
        has_identity_frame = len(identity_hits) > 0 or "做" in text or "为" in text or "是" in text
        # Confidence vs Hedging
        confidence_hits = [w for w in HIGH_CONFIDENCE_WORDS if w in text]
        hedging_hits = [w for w in HEDGING_TABOO_WORDS if w in text]
        # Posing questions
        question_hits = [w for w in SELF_GENERATION_PROMPTS if w in text] or ("？" in text or "?" in text)
        # Emotion high arousal
        arousal_hits = [w for w in HIGH_AROUSAL_WORDS if w in text]
        dominance_hits = [w for w in HIGH_DOMINANCE_WORDS if w in text]

        sub_score = 65.0
        if identity_hits:
            sub_score += 15.0
        if confidence_hits:
            sub_score += 10.0
        if question_hits:
            sub_score += 10.0
        if arousal_hits or dominance_hits:
            sub_score += 10.0
        if hedging_hits:
            sub_score -= 20.0

        score = min(100.0, max(25.0, sub_score))

        return {
            "score": round(score, 1),
            "identity_frames": identity_hits,
            "confidence_cues": confidence_hits,
            "hedging_taboos": hedging_hits,
            "question_prompts": question_hits,
            "arousal_dominance_cues": arousal_hits + dominance_hits,
            "verdict": "👑 极高转化势能 (强身份锚定与高确定感)" if score >= 85 else (
                "🌟 表现良好，心智说服力充足" if score >= 70 else "⚠️ 缺乏身份归属感或存在犹疑套话"
            )
        }

    def audit_lcm_hierarchy(self, text: str) -> Dict[str, Any]:
        """Semin & Fiedler: Linguistic Category Model (DAV vs IAV vs SV vs ADJ)."""
        dav_hits = [w for w in LCM_DAVS if w in text]
        iav_hits = [w for w in LCM_IAVS if w in text]
        sv_hits = [w for w in LCM_SVS if w in text]
        adj_hits = [w for w in LCM_ABSTRACT_ADJS if w in text]

        score = 80.0
        if dav_hits:
            score += len(dav_hits) * 8.0
        if iav_hits:
            score += len(iav_hits) * 5.0
        if adj_hits:
            score -= len(adj_hits) * 15.0

        score = min(100.0, max(30.0, score))

        return {
            "score": round(score, 1),
            "dav_action_verbs": dav_hits,
            "iav_interpretative_verbs": iav_hits,
            "sv_state_verbs": sv_hits,
            "abstract_adjectives_penalized": adj_hits,
            "verdict": "💎 描述性行为动词驱动，阻力极小" if (dav_hits and not adj_hits) else (
                "⚠️ 检测到空洞形容词夸大，建议替换为微观具体行为动词" if adj_hits else "🎯 动词比例健康"
            )
        }

    def audit_regulatory_focus(self, text: str) -> Dict[str, Any]:
        """E. Tory Higgins: Promotion Focus vs. Prevention Focus."""
        pro_hits = [w for w in PROMOTION_WORDS if w in text]
        prev_hits = [w for w in PREVENTION_WORDS if w in text]

        if pro_hits and not prev_hits:
            dominant = "🚀 促进聚焦 (Promotion Focus - 渴望成长/探索收益)"
            primary_fit = "适合新锐尝鲜、进取破局、自我超越人群"
        elif prev_hits and not pro_hits:
            dominant = "🛡️ 预防聚焦 (Prevention Focus - 安全底气/责任规避)"
            primary_fit = "适合抗衰维稳、家庭责任、安全信赖人群"
        elif pro_hits and prev_hits:
            dominant = "⚖️ 双元调和 (Promotion + Prevention Dual Dynamic)"
            primary_fit = "既给突破欲望，又给坚固底气"
        else:
            dominant = "🕊️ 中性平实 (Neutral Reflective)"
            primary_fit = "通用情绪平叙"

        return {
            "dominant_focus": dominant,
            "promotion_tokens": pro_hits,
            "prevention_tokens": prev_hits,
            "audience_fit_advice": primary_fit
        }

    def audit_sound_symbolism(self, text: str) -> Dict[str, Any]:
        """Ramachandran & Hubbard: Bouba-Kiki cross-modal phonetic synaesthesia."""
        kiki_sharp_chars = ["破", "劈", "特", "克", "尖", "极", "精", "晶", "切", "一", "气", "力", "梯", "踢"]
        bouba_round_chars = ["润", "暖", "绵", "梦", "浓", "丰", "满", "漫", "融", "醇", "厚", "温", "安", "舒"]

        kiki_hits = [c for c in kiki_sharp_chars if c in text]
        bouba_hits = [c for c in bouba_round_chars if c in text]

        if len(kiki_hits) > len(bouba_hits):
            aura = "⚡ 奇奇型 (Kiki) · 尖锐/极速/锋芒/高科技感"
        elif len(bouba_hits) > len(kiki_hits):
            aura = "☁️ 布巴型 (Bouba) · 温润/包容/醇厚/安全感"
        else:
            aura = "☯️ 刚柔并济 (Balanced Phonetic Contour)"

        return {
            "phonetic_aura": aura,
            "kiki_sharp_tokens": kiki_hits,
            "bouba_round_tokens": bouba_hits
        }

    def audit_full_psycholinguistics(self, text: str, target_focus: str = "") -> Dict[str, Any]:
        """Synthesize all dimensions into a unified Psycholinguistic Activation Score (0 - 100)."""
        emb = self.audit_embodied_simulation(text)
        som = self.audit_somatic_marker(text)
        spe = self.audit_berger_speacc(text)
        lcm = self.audit_lcm_hierarchy(text)
        reg = self.audit_regulatory_focus(text)
        snd = self.audit_sound_symbolism(text)

        # Weighted Composite Score
        # Embodied (25%), SPEACC (25%), LCM (20%), Somatic Marker (15%), Regulatory & Sound (15%)
        composite = round(
            emb["score"] * 0.25 +
            spe["score"] * 0.25 +
            lcm["score"] * 0.20 +
            som["score"] * 0.15 +
            (85.0 if reg["promotion_tokens"] or reg["prevention_tokens"] else 70.0) * 0.15,
            1
        )

        tier = "👑 神经强共振级 (Neural Resonance S+)" if composite >= 85 else (
            "🌟 认知跃迁级 (Cognitive Shift A+)" if composite >= 75 else (
                "🎯 达标唤醒级 (Competent Activation B)" if composite >= 65 else "⚠️ 弱刺激钝化级 (Blunted Impact C)"
            )
        )

        elevations = self.generate_neuro_elevations(text, reg["dominant_focus"])

        return {
            "text": text,
            "composite_activation_score": composite,
            "activation_tier": tier,
            "embodied_simulation": emb,
            "somatic_marker": som,
            "berger_speacc": spe,
            "lcm_hierarchy": lcm,
            "regulatory_focus": reg,
            "sound_symbolism": snd,
            "neuro_elevations": elevations
        }

    def generate_neuro_elevations(self, text: str, dominant_focus: str) -> List[Dict[str, str]]:
        """Generate 2 neurologically supercharged elevations based on psychology papers."""
        clean = re.sub(r"[，。！？、\s]", "", text)
        half = len(clean) // 2 if len(clean) >= 6 else len(clean)
        p1 = clean[:half]
        p2 = clean[half:]

        return [
            {
                "strategy": "身心具身与动作拟真格 (Embodied Action Simulation)",
                "slogan": f"踩碎日常的锁，把{p2 or '底牌'}稳稳握在手心",
                "neuro_rationale": "运用‘踩碎/锁/握/手心’等高强度描述性动作动词 (LCM-DAV) 触发躯体运动与触觉神经元同时放电，彻底瓦解心智防御。"
            },
            {
                "strategy": "名词身份锚定与高确定格 (Berger Identity & Certainty)",
                "slogan": f"做掌控节奏的人，生活终将向清醒者低头",
                "neuro_rationale": "将动词升级为‘做掌控节奏的人/清醒者’(Bryan & Berger Identity Framing)，并嵌入‘终将’(High-Confidence Cue)，促使受众为维持理想自我认同而自发转化。"
            }
        ]

    def render_markdown_section(self, result: Dict[str, Any]) -> str:
        """Render beautifully formatted markdown section for strategy cards."""
        emb = result["embodied_simulation"]
        som = result["somatic_marker"]
        spe = result["berger_speacc"]
        lcm = result["lcm_hierarchy"]
        reg = result["regulatory_focus"]
        snd = result["sound_symbolism"]

        return f"""> 🧠 **认知神经与心理语言学激活审计 (Psycholinguistic Activation)**:
> - 综合神经激活指数: `★ {result['composite_activation_score']} / 100` ({result['activation_tier']})
> - 具身神经拟真度 (Pulvermüller): `★ {emb['score']}` | {emb['verdict']} (运动/感官词: `{'/'.join(emb['motor_hits'] + emb['sensory_hits']) or '无'}`)
> - 躯体标记释怀比 (Damasio): `★ {som['score']}` | {som['verdict']}
> - SPEACC 转化势能 (Jonah Berger): `★ {spe['score']}` | 身份锚定: `{'/'.join(spe['identity_frames']) or '无'}` | 确定性: `{'/'.join(spe['confidence_cues']) or '无'}`
> - 动词具身层级 (Semin & Fiedler LCM): `★ {lcm['score']}` | {lcm['verdict']}
> - 动机语境匹配 (Higgins RFT): {reg['dominant_focus']} ({reg['audience_fit_advice']})
> - 语音联觉通感 (Bouba-Kiki): {snd['phonetic_aura']}"""


if __name__ == "__main__":
    activator = PsycholinguisticActivator()
    sample = "白天替体面演戏，夜晚让珀莱雅守护真实。"
    res = activator.audit_full_psycholinguistics(sample)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("\nMarkdown Render:")
    print(activator.render_markdown_section(res))
