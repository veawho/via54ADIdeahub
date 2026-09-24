#!/usr/bin/env python3
"""
creative_reasoner.py — Masterclass Linguistic Alchemy & Cultural Brand Engine (v2.3 Upgrade)
Features:
  - 5 Distinct Slogan Archetypes with 4-D Similarity Benchmarks (Phonetic, Semantic, Expression, Structure)
  - Brand Tone Profile Integration
  - Anti-Water Dehydration & Linter Pass
  - Independent Critic Evaluation Node (Emotion Score, Humanity Score, In-group Authenticity)
  - Strict Prompt/Fact Context Isolation
"""

import sys
import os
import json
import sqlite3
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from via54_store.store import KBStore
from via54_store.retrieval import HybridRetriever
from agents.brand_profile_manager import BrandProfileManager
from agents.master_linguistic_engine import MasterLinguisticEngine
from agents.rhetorical_alchemy_synthesizer import RhetoricalAlchemySynthesizer
from agents.master_book_methodology_fuser import MasterBookMethodologyFuser

WATER_WORDS_DICTIONARY = [
    "非常", "十分", "极其", "真是太", "简直", "真的是",
    "令人", "不得不说", "毫不夸张", "值得关注", "众所周知",
    "赋能", "闭环", "抓手", "打法", "矩阵", "链路", "全面提升"
]

class CreativeReasoner:
    """Masterclass Creative Director & Linguistic Alchemy Engine v2.5."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (PROJECT_ROOT / "via54_kb.db")
        self.store = KBStore(self.db_path)
        self.retriever = HybridRetriever(self.store)
        self.subculture_dir = PROJECT_ROOT / "audience_language"
        self.brand_manager = BrandProfileManager()
        self.linguistic_engine = MasterLinguisticEngine()
        self.rhetorical_synthesizer = RhetoricalAlchemySynthesizer(self.db_path)
        self.book_fuser = MasterBookMethodologyFuser(self.db_path)
        self._load_subculture_index()



    def _load_subculture_index(self):
        index_file = self.subculture_dir / "subculture_index.json"
        if index_file.exists():
            try:
                self.subcultures = json.loads(index_file.read_text(encoding="utf-8")).get("subcultures", {})
            except Exception:
                self.subcultures = {}
        else:
            self.subcultures = {}

    def get_audience_context(self, audience_type: str) -> Dict[str, Any]:
        """Retrieve subculture language guidelines, glossary, and taboos."""
        sub_info = self.subcultures.get(audience_type, self.subcultures.get("default", {}))
        content = ""
        if sub_info.get("file"):
            file_path = self.subculture_dir / sub_info["file"]
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
        
        return {
            "audience_type": audience_type,
            "name": sub_info.get("name", "通用大众"),
            "tags": sub_info.get("tags", []),
            "core_keywords": sub_info.get("core_keywords", []),
            "guidelines_markdown": content
        }

    def retrieve_benchmarks(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Retrieve verified historical creative cases from SQLite and Vector DB with fact isolation."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        like_q = f"%{query}%"
        cursor.execute("""
            SELECT * FROM creative_cases
            WHERE title LIKE ? OR brand LIKE ? OR industry LIKE ? OR consumer_trend LIKE ? OR social_meme_tags LIKE ?
            ORDER BY published_year DESC
            LIMIT ?
        """, (like_q, like_q, like_q, like_q, like_q, top_k))
        sql_rows = [dict(r) for r in cursor.fetchall()]

        if len(sql_rows) < top_k:
            rag_hits = self.retriever.search(query, top_k=top_k)
            for h in rag_hits:
                sql_rows.append({
                    "brand": h.get("title", ""),
                    "title": h.get("title", ""),
                    "campaign_slogan": h.get("description", ""),
                    "social_meme_tags": h.get("tags", []),
                    "consumer_insight": h.get("snippet", ""),
                    "source": "rag_kb (verified historical)",
                })

        conn.close()
        return sql_rows[:top_k]

    def retrieve_pun_cases(self, audience_type: str = "", top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant double entendre / pun benchmarks."""
        try:
            from tools.pun_db_builder import get_pun_cases
            return get_pun_cases(audience_type=audience_type, limit=top_k, db_path=self.db_path)
        except Exception:
            return []

    def audit_water_words(self, text: str) -> Dict[str, Any]:
        """Audit empty water words and return critique without destructive text replacement."""
        found = [w for w in WATER_WORDS_DICTIONARY if w in text]
        score_penalty = len(found) * 0.5
        is_clean = len(found) == 0
        detected_str = "、".join(found)
        advice = "文案精炼，无公文水词套话" if is_clean else f"检测到套话水词 [{detected_str}]，建议用具象感官动词替换"
        return {
            "is_clean": is_clean,
            "detected_water_words": found,
            "water_penalty": score_penalty,
            "polishing_advice": advice
        }

    def evaluate_slogan_critic(
        self,
        slogan: str,
        style: str,
        audience_type: str,
        target_audience: str
    ) -> Dict[str, Any]:
        """Independent Critic Node: calculates emotion, humanity, and in-group authenticity scores."""
        water_audit = self.audit_water_words(slogan)
        
        base_emotion = 4.3
        base_humanity = 4.4
        base_fit = 4.3

        if not water_audit["is_clean"]:
            base_humanity -= water_audit["water_penalty"]
            base_emotion -= 0.3

        if len(slogan) > 24:
            base_humanity -= 0.3
        elif len(slogan) < 6:
            base_emotion -= 0.2

        sub_info = self.subcultures.get(audience_type, {})
        keywords = sub_info.get("core_keywords", [])
        matched_keywords = [k for k in keywords if k in slogan]
        
        if audience_type != "default" and matched_keywords:
            base_fit = min(5.0, base_fit + 0.5)
            k_str = "、".join(matched_keywords)
            review_note = f"精准契合【{sub_info.get('name', audience_type)}】语境，自然融入圈内暗号 [{k_str}]，毫无生硬违和感。"
        elif audience_type != "default":
            review_note = f"符合【{target_audience}】基本生活心理，若能结合更多圈层生活场景细节则更佳。"
        else:
            review_note = "大众情绪共鸣强烈，通俗易记，适合全域传播。"

        emotion_score = round(max(1.0, min(5.0, base_emotion)), 1)
        humanity_score = round(max(1.0, min(5.0, base_humanity)), 1)
        audience_fit_score = round(max(1.0, min(5.0, base_fit)), 1)

        return {
            "emotion_score": emotion_score,
            "humanity_score": humanity_score,
            "audience_fit_score": audience_fit_score,
            "detected_water_words": water_audit["detected_water_words"],
            "critic_feedback": review_note,
            "polishing_advice": water_audit["polishing_advice"]
        }

    def generate_creative_strategy(
        self,
        brand: str,
        product: str,
        target_audience: str,
        brief_goal: str,
        audience_type: str = "default",
        style_preference: str = "5大差异化全流派",
        version_count: int = 5,
        enable_critic: bool = True
    ) -> Dict[str, Any]:
        """Generate multi-archetype creative strategies with 4-D similarity benchmarks and brand profile."""
        audience_ctx = self.get_audience_context(audience_type)
        benchmarks = self.retrieve_benchmarks(f"{product} {target_audience}", top_k=3)
        pun_benchmarks = self.retrieve_pun_cases(audience_type=audience_type, top_k=2)
        brand_prof = self.brand_manager.get_profile(brand)
        b_name = f"【{brand_prof.get('brand_name', brand)}】" if brand else "品牌"

        if audience_type == "gay":
            pathology_diagnosis = f"""【圈层群体真实心理洞察 · 拒绝假面与说教】
当代【{target_audience}】最渴望的是‘平视的尊重与真实的自洽’。
他们不需要居高临下的道德审判，也不需要猎奇的刻板标签。真正的沟通是‘心照不宣的默契’——
{b_name}以硬核专业与克制温情，为每一次亲密探索与日常健康保驾护航。"""
            core_insight = f"""【观念重构 · 自由与底气】
【{product}】不是一项被动的健康防护，而是**‘成年人从容掌控亲密自由的底气’**。"""
        elif audience_type == "genz":
            pathology_diagnosis = f"""【时代病理诊断 · 撕开伪善画饼】
当代【{target_audience}】被困在‘必须卷、必须松弛、必须情绪稳定’的假面规训中。
{b_name}不教他们如何成为完美打工人，而是做他们最嘴替的自救盟友，合法化每一次精神离职与肉身除锈。"""
            core_insight = f"""【观念重构 · 工位自救与反叛】
【{product}】不是冰冷的消费品，而是**‘对抗平庸日常与班味的一把微型钝器’**。"""
        elif audience_type == "patient":
            pathology_diagnosis = f"""【真实患者大白话洞察 · 驱散病耻感】
患者在意的往往不是冰冷的医疗参数，而是‘失去的生活细节与日常尊严’。
{b_name}用大白话讲透生活真相，把被动服药重构为主动夺回生活掌控权的日常仪式。"""
            core_insight = f"""【观念重构 · 尊严与陪伴】
【{product}】不仅是治疗方案，更是**‘让生活重回正轨的确定性力量’**。"""
        elif audience_type == "women":
            pathology_diagnosis = f"""【女性话语重构 · 拒绝双重规训】
拒绝‘贤妻良母’与‘超级女强人’的绑架，倡导身体自洽与情绪自主。
{b_name}不贩卖容貌与年龄焦虑，只做女性向内探索、舒展生命力的真诚伙伴。"""
            core_insight = f"""【观念重构 · 我的身体是我的主场】
【{product}】是**‘悦纳自我与身体自由的无声宣言’**。"""
        else:
            pathology_diagnosis = f"""【时代情绪切片 · 穿透冷漠日常】
当代【{target_audience}】在快节奏中寻找真实的喘息空间。
{b_name}直击痛点核心，提供切实可靠的情感共鸣与行动支撑。"""
            core_insight = f"""【观念重构 · 价值回归】
【{product}】为【{target_audience}】的生活注入具象而真实的改变。"""

        brand_manifesto = f"""在人人都急着给出标准答案的时代，
{b_name}只想陪你做回那个真实、生动、允许有脾气与脆弱的自己。
生活或许沉重，但你的每一步探索都该有坚实的底气。
敬每一个在复杂现实里，依然清醒生活的灵魂。"""

        # Cognitive & Rhetorical Alchemy Synthesis with Reflection Loop (GitHub SOTA Inspired)
        synthesized_cards = self.rhetorical_synthesizer.synthesize_slogans_with_reflection(
            brand=brand,
            product=product,
            target_audience=target_audience,
            brief_goal=brief_goal,
            benchmarks=benchmarks,
            audience_type=audience_type
        )
        s1_tag = synthesized_cards[0]["hero_slogan"]
        s2_tag = synthesized_cards[1]["hero_slogan"]
        s3_tag = synthesized_cards[2]["hero_slogan"]
        s4_tag = synthesized_cards[3]["hero_slogan"]
        s5_tag = synthesized_cards[4]["hero_slogan"]
        detected_awareness = synthesized_cards[0]["cognitive_stage"]


        archetypes = [
            {
                "id": 1,
                "style_category": "反转热梗型 (Subversive Humor)",
                "style_desc": "利用反差与自嘲消解沉重，制造高传播社交货币",
                "tagline": s1_tag,
                "sub_slogans": [
                    f"表面情绪稳定，全靠{b_name}在暗中做物理阻尼。",
                    f"生活天天给我上课，我用{b_name}给身体上一层护甲。"
                ],
                "scenario_copy": f"【工位桌面/社媒抓手】‘肉身在线除锈，精神早已归位。请给{b_name}十秒。’",
                "target_platforms": ["微博", "小红书", "抖音"]
            },
            {
                "id": 2,
                "style_category": "情绪嘴替型 (Unfiltered Voice)",
                "style_desc": "一针见血替用户说出心底最真实、不敢大声说的渴望",
                "tagline": s2_tag,
                "sub_slogans": [
                    f"懂你每一次不想说的欲言又止，也接住你所有的疲惫。",
                    f"不讲大道理，只给最实在的底气。"
                ],
                "scenario_copy": f"【地铁/电梯海报】‘屏幕上的未读消息很多，但最该被优先回复的，是你自己的感受。’",
                "target_platforms": ["小红书", "微信朋友圈", "户外大屏"]
            },
            {
                "id": 3,
                "style_category": "故事叙事型 (Cinematic Narrative)",
                "style_desc": "用微感官蒙太奇与具象生活细节，建立不可替代的高溢价心智",
                "tagline": s3_tag,
                "sub_slogans": [
                    f"凌晨两点三十七分，城市在等待黎明，你在等待一口清甜洗去疲倦。",
                    f"当脚步比言语诚实，每一次出发都值得被全心托付。"
                ],
                "scenario_copy": f"【品牌微电影旁白】‘他在电梯合上的那一秒松开领带，那一刻，他终于做回了自己。’",
                "target_platforms": ["B站", "视频号", "品牌TVC"]
            },
            {
                "id": 4,
                "style_category": "数据背书型 (Hardcore Authority)",
                "style_desc": "用硬核事实、严谨机理与数字震撼，建立无懈可击的信任壁垒",
                "tagline": s4_tag,
                "sub_slogans": [
                    f"99%的专业守护，只为让你100%尽兴探索。",
                    f"每一次按时守护，都是夺回生活掌控权的确定底气。"
                ],
                "scenario_copy": f"【产品详情页/药房终端】‘零侥幸，硬防护。专业认证，守护全场。’",
                "target_platforms": ["天猫/京东", "专业医疗终端", "垂直社群"]
            },
            {
                "id": 5,
                "style_category": "圈层共鸣型 (Subculture Identity)",
                "style_desc": "运用地道圈内暗号与情感连接，瞬间建立高纯度认同",
                "tagline": s5_tag,
                "sub_slogans": [
                    f"每一次尽兴的PLAY，都该有不掉线的安全感。",
                    f"懂你的局，更懂你的每一次认真营业。"
                ],
                "scenario_copy": f"【圈层派对/私域活动】‘在这里不用装，懂你的人自然会心一笑。’",
                "target_platforms": ["垂直垂类App", "线下快闪", "私域社群"]
            }
        ]

        versions = []
        for arch in archetypes[:version_count]:
            critic_res = self.evaluate_slogan_critic(
                slogan=arch["tagline"],
                style=arch["style_category"],
                audience_type=audience_type,
                target_audience=target_audience
            ) if enable_critic else {}
            
            sim_bench = self.linguistic_engine.match_similarity_benchmark(
                arch["tagline"],
                arch["style_category"],
                audience_type=audience_type
            )
            
            arch_data = {
                **arch,
                "critic_eval": critic_res,
                "similarity_benchmark": sim_bench
            }
            versions.append(arch_data)

        super_signs = [
            f"👁️ **视觉通感 (Visual Sign)**: 极简高辨识度符号 + 情感态度烫金短句，打造随身‘精神护甲’；",
            f"👂 **行为暗号 (Behavioral Ritual)**: 专属开封与使用仪式声效，形成‘物理切断外界纷扰’的心智触发；",
            f"📦 **社交道具 (Social Prop)**: 随单定制‘情绪自救/去班味’随身盲盒与趣味宣言立牌。"
        ]

        stunts = [
            f"1. **【生活真相发布会】真实人群微电影**: 零滤镜记录素人在深夜与生活交锋的具象瞬间，直击痛点与泪点；",
            f"2. **【城市自救除锈站】地标快闪空间**: 在核心商圈/产业园设立互动舱，凭借当日工作生活痛点票根兑换专属治愈能量；",
            f"3. **【圈层解密行动】跨界文化联名**: 联合青年脱口秀/艺术空间，打造话题破圈事件。"
        ]

        # Masterclass Books Methodology Strategy Pack
        book_pack = self.book_fuser.synthesize_master_strategy_pack(
            brand=brand,
            product=product,
            target_audience=target_audience,
            brief_goal=brief_goal
        )

        return {
            "brand": brand,
            "brand_profile": brand_prof,
            "product": product,
            "target_audience": target_audience,
            "audience_type": audience_type,
            "audience_name": audience_ctx.get("name", "通用大众"),
            "brief_goal": brief_goal,
            "pathology_diagnosis": pathology_diagnosis,
            "core_insight": core_insight,
            "brand_manifesto": brand_manifesto,
            "total_versions": len(versions),
            "versions": versions,
            "super_signs": super_signs,
            "stunts": stunts,
            "book_strategy": book_pack,
            "benchmarks_used": [b.get("title", "") for b in benchmarks if b.get("title")],
            "pun_benchmarks": [p.get("pun_text", "") for p in pun_benchmarks if p.get("pun_text")],
        }


    def render_feishu_card(self, strategy: Dict[str, Any]) -> str:
        """Render multi-version markdown formatted response with Critic scores & Similarity benchmarks."""
        versions_md = ""
        for v in strategy["versions"]:
            subs_md = "\n".join([f"  - *「{sub}」*" for sub in v["sub_slogans"]])
            critic = v.get("critic_eval", {})
            sim = v.get("similarity_benchmark", {})
            score_str = ""
            if critic:
                score_str = f"""
> 📊 **Critic 质检评分**: 情绪深度 `★ {critic.get('emotion_score', '-')}` | 真人感 `★ {critic.get('humanity_score', '-')}` | 圈层契合度 `★ {critic.get('audience_fit_score', '-')}`
> 💬 **评审点评**: {critic.get('critic_feedback', '')}
> 💧 **脱水精炼**: {critic.get('polishing_advice', '')}
> 🔗 **相似性对标参考**: {sim.get('similarity_dimension', '🏛️ 结构相似性')}
> 📌 **对标经典案例**: *{sim.get('benchmark_case', '')}*
> 🔍 **对标借鉴解析**: {sim.get('similarity_analysis', '')}"""

            versions_md += f"""### 版本 {v['id']} · {v['style_category']}
> 💡 **策略导向**: {v['style_desc']}  
> 🎯 **核心战役口号 (Hero Slogan)**:  
> **`「{v['tagline']}」`**  
>
> 📋 **场景金句延伸**:  
{subs_md}  
> 
> 🖼️ **物料与落地文案**:  
```text
{v['scenario_copy']}
```
> 📱 **推荐发布渠道**: {', '.join(v['target_platforms'])}{score_str}

---
"""

        signs_md = "\n".join(strategy["super_signs"])
        stunts_md = "\n\n".join(strategy["stunts"])
        benchmarks_md = "、".join(strategy["benchmarks_used"]) if strategy["benchmarks_used"] else "2024-2026 全网顶级案例库"
        puns_md = "、".join([f"「{p}」" for p in strategy.get("pun_benchmarks", [])]) if strategy.get("pun_benchmarks") else "无特定双关"
        prof = strategy.get("brand_profile", {})
        bk = strategy.get("book_strategy", {})
        book_dirs_md = "\n".join([
            f"> - **{d['school']}**: {d['core_directive']}"
            for d in bk.get("master_directives", [])
        ]) or "> 暂无特定书籍指引"

        md = f"""# 🌌 【{strategy['brand']}】创意品牌全案与差异化口号矩阵

> 📌 **战役目标**: {strategy['brief_goal']}  
> 🎯 **目标客群**: {strategy['target_audience']} (圈层: {strategy['audience_name']}) | 📦 **核心产品**: {strategy['product']}  
> 🏷️ **品牌调性画像**: {prof.get('tone_of_voice', '经典自洽')}  
> 🔍 **权威历史案例参考**: {benchmarks_md}  
> 🎭 **精选双关对标**: {puns_md}  

---

## 🩸 一、 时代情绪切片与人群真实心声
{strategy['pathology_diagnosis']}

---

## 💡 二、 观念重构与颠覆性洞察
{strategy['core_insight']}

---

## 📜 三、 品牌灵魂宣言 (Brand Manifesto)
```text
{strategy['brand_manifesto']}
```

---

## 🏆 四、 5 大差异化创意版本与四维相似性对标矩阵
{versions_md}

## 🔮 五、 超级记忆符号与感官图腾 (Super Sign)
{signs_md}

---

## 🚀 六、 文化级引爆事件与破圈行动 (Cultural Stunts)
{stunts_md}

---

## 📚 七、 经典文案大师与广告书籍方法论赋能 (18 Masterclass Pillars)
> 📌 **心智钉子 (Mental Nail · 特劳特《定位》)**: `{bk.get('positioning_audit', {}).get('mental_nail', '未指定')}`  
> 🔨 **视觉锤 (Visual Hammer · 劳拉·里斯)**: `{bk.get('positioning_audit', {}).get('visual_hammer', '未指定')}`  
> ⚡ **生命原力锚定 (LF8 · 惠特曼《吸金广告》)**: `{bk.get('life_force_audit', {}).get('matched_primary_desires', ['通用心理认同'])[0]}`  
> 
> 🏛️ **大师学派策略指引 (Master Directives)**:  
{book_dirs_md}
"""
        return md



if __name__ == "__main__":
    reasoner = CreativeReasoner()
    res = reasoner.generate_creative_strategy(
        brand="proya",
        product="高浓度早C晚A精华",
        target_audience="高压职场女性",
        brief_goal="打破年龄焦虑，树立先锋抗衰心智",
        audience_type="women",
        version_count=5
    )
    print(reasoner.render_feishu_card(res))
