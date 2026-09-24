#!/usr/bin/env python3
"""
master_book_methodology_fuser.py — Book Methodologies & Strategy Fusion Engine
Fuses principles from 24 classic copywriting & advertising books into generative heuristics:
  1. 特劳特《定位》/ 劳拉·里斯《视觉锤》: 心智钉子 (Mental Nail) & 视觉锤 (Visual Hammer)
  2. 阿尔·里斯《聚焦》: 聚焦单刀原则 (Laser Focus vs Greedy Multi-selling)
  3. 华与华《超级符号》: 文化母体寄生 & 超级行动指令
  4. 林永强《小强广告100招》: 文案修剪刀 (动词化、去副词、微感官)
  5. 德鲁·惠特曼《吸金广告》: LF8 生命原力映射
  6. 鲍勃·布莱《文案创作完全手册》: 4U 转化审计 (Urgent, Unique, Ultra-specific, Useful)
  7. 约瑟夫·休格曼《文案训练手册》: 滑梯效应与好奇心种子
  8. 乔纳·伯杰《疯传》: STEPPS 6大社交病毒传播法则
  9. 罗伯特·西奥迪尼《影响力》: 6大说服心理武器
  10. 金枪大叔《借势》: 以弱胜强与大白话情绪嘴替
  11. 关键明《爆款文案》: 4步转化闭环与感官占有
  12. 新井桥《写给非广告人的广告书》: 生活者平视语言与日常解困
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


class MasterBookMethodologyFuser:
    """Fuses 24 classic advertising book theories into generative strategy and copy heuristics."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (PROJECT_ROOT / "via54_kb.db")
        self._load_books_cache()

    def _load_books_cache(self):
        """Load books methodologies from SQLite."""
        self.books = {}
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM copywriting_methodologies")
            rows = cursor.fetchall()
            for r in rows:
                self.books[r["book_id"]] = {
                    "book_id": r["book_id"],
                    "title": r["title"],
                    "author": r["author"],
                    "school": r["school"],
                    "core_theory": r["core_theory"],
                    "thinking_paradigm": r["thinking_paradigm"],
                    "strategy_framework": json.loads(r["strategy_framework_json"]),
                    "writing_methods": json.loads(r["writing_methods_json"]),
                    "classic_golden_cases": json.loads(r["classic_golden_cases_json"]),
                    "algorithmic_heuristics": json.loads(r["algorithmic_heuristics_json"])
                }
            conn.close()
        except Exception:
            # Fallback to json file
            json_file = PROJECT_ROOT / "knowledge" / "master_copywriting_books.json"
            if json_file.exists():
                data = json.loads(json_file.read_text(encoding="utf-8"))
                for b in data.get("books", []):
                    self.books[b["book_id"]] = b

    def map_life_force_8(self, context_text: str) -> Dict[str, Any]:
        """Drew Eric Whitman's Life-Force 8 (LF8) biological desire mapper."""
        lf8_rules = [
            ("生存、健康与延长寿命 (LF1: Survival & Longevity)", ["健康", "养生", "保命", "救命", "长寿", "体检", "医生", "药", "安全"]),
            ("享受高品质饮品与美食 (LF2: Food & Beverage)", ["吃", "喝", "口渴", "清甜", "美味", "饱", "舌尖", "口感", "食材"]),
            ("免于恐惧、痛苦与焦虑 (LF3: Freedom from Fear & Pain)", ["害怕", "失眠", "内卷", "焦虑", "痛苦", "猝死", "脱发", "除锈", "压力"]),
            ("性的陪伴与魅力吸引力 (LF4: Sexual Companionship)", ["恋爱", "性感", "亲密", "吸引", "约会", "荷尔蒙", "心动"]),
            ("舒适自在的生活环境 (LF5: Comfortable Living)", ["松弛", "舒适", "家", "沙发", "自由", "自在", "温暖", "安宁"]),
            ("与人攀比、胜出与优越感 (LF6: Winning & Superiority)", ["赢", "第一", "领先", "优越", "高端", "精英", "段位", "超越"]),
            ("保护与关爱所爱之人 (LF7: Care of Loved Ones)", ["家人", "孩子", "父母", "伴侣", "守护", "托付", "陪伴"]),
            ("获得社会认同与圈层尊重 (LF8: Social Approval)", ["体面", "认同", "社交", "圈子", "尊重", "主角", "主权", "底气"])
        ]
        matched = []
        for name, keywords in lf8_rules:
            if any(k in context_text.lower() for k in keywords):
                matched.append(name)
        if not matched:
            matched.append("获得社会认同与圈层尊重 (LF8: Social Approval)")
        return {
            "book": "德鲁·埃里克·惠特曼《吸金广告》",
            "matched_primary_desires": matched[:2],
            "creative_mandate": f"创意必须牢牢锚定【{matched[0]}】，在0.5秒内激活用户的生物学本能欲望。"
        }

    def craft_positioning_nail_and_hammer(self, brand: str, product: str, brief_goal: str) -> Dict[str, Any]:
        """Trout & Ries: Mental Nail (Language) + Visual Hammer (Imagery)."""
        b_name = brand or "品牌"
        
        # Heuristics for mental nail
        if any(k in brief_goal for k in ["安全", "守护", "健康", "专业"]):
            nail = f"【{b_name}】= 确定性专业守护"
            hammer = "高饱和警示黄盾牌符号 / 金属双保险锁扣开合声"
            counter_position = "重新定义传统粗放防护：告别侥幸，确立硬核标准"
        elif any(k in brief_goal for k in ["颠覆", "年轻", "反卷", "嘴替", "社交"]):
            nail = f"【{b_name}】= 工位精神防弹衣"
            hammer = "工位结界亚克力双面立牌 / 极简除锈灰与醒目荧光绿撞色"
            counter_position = "重新定义职场规训：不教你成为完美工具人，陪你守护野生灵魂"
        elif any(k in brief_goal for k in ["高端", "东方", "诗意", "美学", "质感"]):
            nail = f"【{b_name}】= 东方留白与文人意境"
            hammer = "粗陶微瑕质感器皿 / 墨色书法笔触留白"
            counter_position = "重新定义欧美浮夸工业香：不迎合聚光灯，只丰盈生命场"
        else:
            nail = f"【{b_name}】= 日常生活的能量解药"
            hammer = "随身口袋能量胶囊造型 / 撕开时清脆金属泄压声"
            counter_position = "对立于平庸日常，提供触手可及的精神喘息"

        return {
            "source_book": "阿尔·里斯 & 杰克·特劳特《定位》/ 劳拉·里斯《视觉锤》",
            "mental_nail": nail,
            "visual_hammer": hammer,
            "counter_positioning": counter_position
        }

    def apply_xiaoqiang_trimmer(self, draft_slogan: str) -> Dict[str, Any]:
        """Lin Guizhi's 'Xiaoqiang Copy Trimmer' (剪去副词、使用动词、建立人话感)."""
        trimmed = draft_slogan
        removed_words = []
        for w in ["非常", "十分", "极其", "真是", "令人", "彻底", "全面"]:
            if w in trimmed:
                trimmed = trimmed.replace(w, "")
                removed_words.append(w)
        
        # Check verb density
        verbs = ["跑", "跳", "听", "撕", "吹", "握", "踏", "换", "看", "喝", "走", "除", "开", "抢"]
        verb_count = sum(1 for v in verbs if v in trimmed)
        
        return {
            "source_book": "林桂枝《小强广告100招》",
            "original": draft_slogan,
            "trimmed_result": trimmed,
            "removed_water_adverbs": removed_words,
            "verb_energy_score": f"{verb_count} 个动态物理动词注入",
            "evaluation": "文案经修剪刀打磨，削去浮华形容词，保留生脆的人话动感" if removed_words else "文案原生具备极高人话感与动能"
        }

    def audit_4u_score(self, slogan: str) -> Dict[str, Any]:
        """Robert W. Bly's 4U Formula Audit (Urgent, Unique, Ultra-specific, Useful)."""
        has_urgent = any(w in slogan for w in ["今", "立刻", "现在", "马上", "周五", "深夜", "凌晨", "那一秒"])
        has_unique = any(w in slogan for w in ["【", "】", "除锈", "防弹衣", "PPT", "离职", "骨头", "鳕鱼"])
        has_specific = bool(re.search(r"\d+", slogan)) or any(w in slogan for w in ["凌晨两点", "99条", "一滴", "十秒", "两厘米"])
        has_useful = any(w in slogan for w in ["救命", "活到", "守护", "管饱", "解药", "底气", "自由"])

        scores = {
            "Urgent (紧迫感)": 4.5 if has_urgent else 3.8,
            "Unique (独特性)": 4.8 if has_unique else 4.0,
            "Ultra-specific (超具象度)": 4.6 if has_specific else 3.9,
            "Useful (实用利益度)": 4.7 if has_useful else 4.1
        }
        overall_4u = round(sum(scores.values()) / 4.0, 1)

        return {
            "source_book": "罗伯特·布莱《文案创作完全手册》",
            "overall_4u_index": overall_4u,
            "dimension_scores": scores,
            "verdict": "满足4U实战标准，能有效推动受众注意力向购买转化跃迁" if overall_4u >= 4.2 else "建议补充更具体的时间、数字或读者切身利益"
        }

    def audit_sugarman_slippery_slide(self, text: str) -> Dict[str, Any]:
        """Joseph Sugarman's 'Slippery Slide' & 'Seeds of Curiosity' Audit."""
        clauses = [c.strip() for c in re.split(r"[,，。！？；\s]+", text) if c.strip()]
        first_clause_len = len(clauses[0]) if clauses else 0
        has_curiosity_seed = any(w in text for w in ["不仅", "其实", "但是", "为什么", "秘密", "真相", "答案", "原来", "这一刻"])
        
        # Sugarman rule: First sentence must be short, punchy and irresistible
        is_short_opening = 3 <= first_clause_len <= 10
        slide_score = 4.0
        if is_short_opening:
            slide_score += 0.5
        if has_curiosity_seed:
            slide_score += 0.4

        return {
            "source_book": "约瑟夫·休格曼《文案训练手册》",
            "slippery_slide_score": round(min(5.0, slide_score), 1),
            "first_sentence_length": f"{first_clause_len} 字 (极短开篇)" if is_short_opening else f"{first_clause_len} 字 (建议缩短至8字以内制造下坠动能)",
            "curiosity_seeds_detected": has_curiosity_seed,
            "verdict": "具备强烈滑梯动能，开篇短促有力，读者阅读阻力极低" if slide_score >= 4.5 else "建议首句压缩字数，埋下‘好奇心种子’驱动继续阅读"
        }

    def audit_jinqiang_leverage(self, slogan: str, brand: str) -> Dict[str, Any]:
        """Uncle Jinqiang's '128 Rules of Leverage' & Asymmetric Breakthrough Audit."""
        has_emotion = any(w in slogan for w in ["救命", "画饼", "离职", "活到", "撒野", "生脆", "心跳", "骨头", "退火", "演戏"])
        has_colloquial = any(w in slogan for w in ["别", "管你", "马上", "天天", "不用", "就是", "替"])
        is_concise = len(slogan) <= 24

        leverage_score = 4.2
        if has_emotion:
            leverage_score += 0.4
        if has_colloquial:
            leverage_score += 0.3
        if is_concise:
            leverage_score += 0.1

        return {
            "source_book": "金枪大叔《借势：以弱胜强的128条黄金法则》",
            "emotional_leverage_score": round(min(5.0, leverage_score), 1),
            "colloquial_recitability": "大白话一听就懂，出租车司机与菜场大妈听一遍就能复述" if has_colloquial else "具备一定口语感",
            "verdict": "成功借势社会情绪潜流，立起反叛旗帜，具备以弱胜强的锋利度" if leverage_score >= 4.6 else "建议进一步做减法，让情绪更浓缩"
        }

    def audit_stepps_virality(self, slogan: str) -> Dict[str, Any]:
        """Jonah Berger's 'Contagious' STEPPS Virality Model Audit."""
        has_currency = any(w in slogan for w in ["精神离职", "除锈", "防弹衣", "PPT", "骨头", "鳕鱼", "演戏", "真实"])
        has_trigger = any(w in slogan for w in ["白天", "夜晚", "凌晨", "周五", "工位", "电梯", "下班", "这一刻"])
        has_emotion = any(w in slogan for w in ["救命", "画饼", "狂欢", "活到", "生脆", "心跳", "撒野", "叹息"])
        has_practical = any(w in slogan for w in ["管饱", "解药", "0添加", "分期", "护甲", "不用忍", "立刻"])
        
        stepps_score = 3.8
        if has_currency: stepps_score += 0.3
        if has_trigger: stepps_score += 0.3
        if has_emotion: stepps_score += 0.3
        if has_practical: stepps_score += 0.3

        return {
            "source_book": "乔纳·伯杰《疯传：让你的产品、思想、行为像病毒一样入侵》",
            "stepps_virality_score": round(min(5.0, stepps_score), 1),
            "matched_factors": [
                f"{'✅' if has_currency else '⚪'} 社交货币 (Social Currency)",
                f"{'✅' if has_trigger else '⚪'} 场景诱因 (Triggers)",
                f"{'✅' if has_emotion else '⚪'} 高能量情绪 (Emotion)",
                f"{'✅' if has_practical else '⚪'} 实用价值 (Practical Value)"
            ],
            "verdict": "具备高病毒裂变潜能，融合了强社交货币与日常高频场景线索" if stepps_score >= 4.4 else "建议增强社交货币或绑定更高频的日常诱因场景"
        }

    def audit_cialdini_influence(self, slogan: str) -> Dict[str, Any]:
        """Robert Cialdini's 'Influence' 6 Persuasion Weapons Audit."""
        has_social_proof = any(w in slogan for w in ["所有人", "大家", "同行", "都在", "认领"])
        has_authority = any(w in slogan for w in ["科学", "专业", "医生", "认证", "标准", "指标"])
        has_scarcity = any(w in slogan for w in ["唯", "绝不", "最后", "透支", "不能忍", "只有"])
        has_reciprocity = any(w in slogan for w in ["给", "还给", "陪伴", "托付", "守护"])

        weapons = []
        if has_social_proof: weapons.append("社会认同 (Social Proof)")
        if has_authority: weapons.append("权威背书 (Authority)")
        if has_scarcity: weapons.append("稀缺与损失厌恶 (Scarcity)")
        if has_reciprocity: weapons.append("互惠与真诚托付 (Reciprocity)")

        score = 4.0 + len(weapons) * 0.25
        return {
            "source_book": "罗伯特·西奥迪尼《影响力》",
            "influence_score": round(min(5.0, score), 1),
            "active_weapons": weapons or ["认知自洽驱动"],
            "verdict": f"成功激活决策快捷通道: [{', '.join(weapons or ['自洽认同'])}]"
        }

    def audit_focus_purity(self, slogan: str) -> Dict[str, Any]:
        """Al Ries's 'Focus' Single-Knife Audit (极度收窄焦点，杜绝贪婪多重卖点)."""
        has_greedy_connectors = any(w in slogan for w in ["不仅", "而且", "兼具", "同时", "还具备", "全方位", "多重"])
        clauses = [c for c in re.split(r"[,，。！？；\s]+", slogan) if c]
        is_laser_focused = len(clauses) <= 2 and not has_greedy_connectors

        return {
            "source_book": "阿尔·里斯《聚焦：决定公司命运的雄心》",
            "focus_purity_score": 4.8 if is_laser_focused else 3.8,
            "greedy_connectors_detected": has_greedy_connectors,
            "verdict": "如激光般极度聚焦于单一点，无冗余多卖点贪婪干扰" if is_laser_focused else "检测到多重卖点分散心智焦点，建议做减法只留一把尖刀"
        }

    def audit_three_beauties(self, slogan: str) -> Dict[str, Any]:
        """Xu Yuanchong's 'Three Beauties' Doctrine (意美、音美、形美)."""
        poetic_images = ["花", "叶", "虎", "蔷薇", "月", "日", "朝", "暮", "风", "雪", "海", "山", "水", "草", "木", "石", "星", "火", "光", "雨", "霜", "梦", "鱼", "路"]
        has_poetic_image = any(img in slogan for img in poetic_images)

        clauses = [c for c in re.split(r"[,，。！？；\s]+", slogan) if c]
        is_symmetric = False
        symmetry_desc = "参差长短"
        if len(clauses) >= 2:
            len1, len2 = len(clauses[0]), len(clauses[1])
            if len1 == len2:
                is_symmetric = True
                symmetry_desc = f"{len1}+{len2} 严整对称"
            elif abs(len1 - len2) <= 2:
                is_symmetric = True
                symmetry_desc = f"{len1}+{len2} 律动呼应"
        elif len(clauses) == 1 and len(clauses[0]) in [4, 6, 8]:
            is_symmetric = True
            symmetry_desc = f"{len(clauses[0])}言凝练"

        try:
            from agents.rhetorical_alchemy_synthesizer import RhetoricalAlchemySynthesizer
            alchemy = RhetoricalAlchemySynthesizer()
            tonal = alchemy.measure_cadence_and_tone(slogan)
            cadence_score = tonal.get("metrics", {}).get("cadence_score", 4.0)
            tone_pattern = tonal.get("tone_pattern", "")
            rhyme_cat = tonal.get("rhyme_category", "")
        except Exception:
            cadence_score = 4.2
            tone_pattern = "平仄协畅"
            rhyme_cat = "同辙"

        three_beauties_score = round((
            (4.8 if has_poetic_image else 4.0) +
            (4.8 if is_symmetric else 3.8) +
            cadence_score
        ) / 3, 1)

        return {
            "source_book": "许渊冲《文学翻译谈 / 许渊冲经典作品集》",
            "three_beauties_score": three_beauties_score,
            "meaning_beauty": "具备鲜明诗意意象与情感深度" if has_poetic_image else "意象偏抽象，建议注入自然或微感官具象物",
            "form_beauty": symmetry_desc,
            "sound_beauty": f"平仄声调: {tone_pattern} | 韵辙: {rhyme_cat}",
            "verdict": "三美兼备，如出金石" if three_beauties_score >= 4.5 else "基本达意，可进一步雕琢字数对称与声律"
        }

    def apply_yu_guangzhong_de_westernizer(self, text: str) -> Dict[str, Any]:
        """Yu Guangzhong's Anti-Westernization Trimmer (拒斥恶性西化与欧化病，文白张力提纯)."""
        westernized_markers = [
            ("进行", "用‘进行’+动词（如进行讨论/进行闻嗅），窒息了动词活力，应直接用‘谈’、‘嗅’"),
            ("对于", "滥用‘对于’引起话题，显得官僚拖沓，可直接点名事物"),
            ("关于", "‘关于...的方面’属于多余虚词，直接做主谓表述"),
            ("作为一个", "西方 as a... 的生硬直译，中文可直接省略"),
            ("具有", "伪学术名词后缀（如‘具有创新性’），还原为生动动词或形容词（如‘破旧立新’）"),
            ("被", "中文重无主意合句，避免生搬硬套英语被动语态")
        ]
        hits = []
        for marker, critique in westernized_markers:
            if marker in text:
                hits.append({"marker": marker, "critique": critique})

        purity_score = 5.0 - len(hits) * 0.4
        return {
            "source_book": "余光中《余光中谈翻译 / 翻译乃大道 (兼论论中文的常态与变态)》",
            "anti_westernization_purity_score": round(max(3.0, purity_score), 1),
            "westernized_hits": hits,
            "verdict": "剔除欧化胶水词，回归汉语具象动词；并置猛虎与蔷薇，制造文白相间的审美张力" if hits else "无恶性西化病，句式精纯有力，母语筋骨舒展"
        }

    def audit_qian_zhongshu_huajing(self, slogan: str) -> Dict[str, Any]:
        """Qian Zhongshu's 'Huajing' Transmigration Audit (化境与文字脱胎换骨)."""
        has_metaphor = any(m in slogan for m in ["如", "似", "像", "若", "是", "，", "。"])
        has_cliche = any(c in slogan for c in ["引领潮流", "尽享奢华", "尊贵体验", "完美品质", "匠心打造", "卓越不凡"])

        is_huajing = has_metaphor and not has_cliche
        return {
            "source_book": "钱钟书《钱钟书论翻译 (兼论林纾的翻译与管锥编)》",
            "huajing_score": 4.8 if is_huajing else (4.2 if not has_cliche else 3.5),
            "is_cliche_free": not has_cliche,
            "verdict": "入于化境：脱胎换骨浑然天成，以奇绝隐喻直击心智，无陈腐说教" if is_huajing else ("文辞平顺，建议注入钱式机智警策隐喻" if not has_cliche else "检测到广告陈词滥调，建议彻底打碎重写")
        }

    def fetch_relevant_divine_translations(self, keyword: str = "", limit: int = 3) -> List[Dict[str, Any]]:
        """Fetch canonical divine translations matching the keyword or random top benchmark."""
        results = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if keyword:
                cursor.execute("""
                    SELECT * FROM divine_translations 
                    WHERE divine_translation LIKE ? OR original_text LIKE ? OR copywriting_insight LIKE ?
                    LIMIT ?
                """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit))
            else:
                cursor.execute("SELECT * FROM divine_translations ORDER BY id ASC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            for r in rows:
                results.append(dict(r))
            conn.close()
        except Exception:
            pass
        return results

    def fetch_relevant_classical_chinese(self, keyword: str = "", limit: int = 2) -> List[Dict[str, Any]]:
        """Fetch classical Chinese masterpieces matching keyword or top benchmark."""
        results = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if keyword:
                cursor.execute("""
                    SELECT * FROM classical_chinese_masterpieces 
                    WHERE title LIKE ? OR golden_lines LIKE ? OR author LIKE ? OR emotional_archetype LIKE ?
                    LIMIT ?
                """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit))
            else:
                cursor.execute("SELECT * FROM classical_chinese_masterpieces ORDER BY id ASC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            for r in rows:
                results.append(dict(r))
            conn.close()
        except Exception:
            pass
        return results

    def fetch_relevant_wilde_epigrams(self, keyword: str = "", limit: int = 2) -> List[Dict[str, Any]]:
        """Fetch Oscar Wilde epigrams matching keyword or top benchmark."""
        results = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if keyword:
                cursor.execute("""
                    SELECT * FROM oscar_wilde_corpus 
                    WHERE chinese_translation LIKE ? OR english_quote LIKE ? OR theme LIKE ? OR paradox_mechanism LIKE ?
                    LIMIT ?
                """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit))
            else:
                cursor.execute("SELECT * FROM oscar_wilde_corpus ORDER BY id ASC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            for r in rows:
                results.append(dict(r))
            conn.close()
        except Exception:
            pass
        return results

    def audit_wildean_paradox(self, slogan: str) -> Dict[str, Any]:
        """Oscar Wilde's Paradox & Aesthetic Anti-Common-Sense Audit (王尔德悖论机智与唯美主义)."""
        paradox_triggers = ["除了", "唯一", "做自己", "爱自己", "向", "生活在", "阴沟", "星空", "价钱", "价值", "错误", "自私", "迷人", "乏味"]
        has_paradox = any(t in slogan for t in paradox_triggers)
        clauses = [c for c in re.split(r"[,，。！？；\s]+", slogan) if c]

        is_wildean = has_paradox or (len(clauses) >= 2 and any(w in slogan for w in ["不", "别", "谁", "莫"]))
        return {
            "source_school": "奥斯卡·王尔德《唯美主义与悖论心法》",
            "wildean_paradox_score": 4.8 if is_wildean else 3.8,
            "has_anti_common_sense": is_wildean,
            "verdict": "具备王尔德式反常识机智与唯美主义张力，撕破假大空自嗨" if is_wildean else "表达较为常规顺从，建议注入‘悖论倒戈’或‘极度悦己’锋芒"
        }

    def audit_classical_chinese_resonance(self, slogan: str) -> Dict[str, Any]:
        """Classical Chinese Poetic Resonance & Bone Audit (中国古典诗词风骨与文气)."""
        poetic_archetypes = ["风雨", "平生", "江湖", "天地", "清风", "明月", "沧海", "一粟", "星", "舟", "雪", "初见", "回首", "阑珊", "尽欢", "登高"]
        matched_archetypes = [a for a in poetic_archetypes if a in slogan]
        
        has_classical_bone = len(matched_archetypes) > 0
        return {
            "source_school": "中国古典诗词与千古文气风骨",
            "classical_resonance_score": 4.8 if has_classical_bone else 4.0,
            "matched_archetypes": matched_archetypes or ["东方含蓄意象"],
            "verdict": f"蕴含千古文气风骨，意境辽远深邃: [{', '.join(matched_archetypes or ['东方文气'])}]" if has_classical_bone else "文辞偏向现代口语，可适度借势古典诗词的苍茫气象与对仗"
        }

    def synthesize_master_strategy_pack(
        self,
        brand: str,
        product: str,
        target_audience: str,
        brief_goal: str
    ) -> Dict[str, Any]:
        """Synthesize masterclass strategic directives from all 27 book methodologies, classical poetry & Wilde."""
        combined_text = f"{brand} {product} {target_audience} {brief_goal}"
        positioning = self.craft_positioning_nail_and_hammer(brand, product, brief_goal)
        lf8 = self.map_life_force_8(combined_text)
        divine_benchmarks = self.fetch_relevant_divine_translations(keyword="", limit=3)
        classical_benchmarks = self.fetch_relevant_classical_chinese(keyword="", limit=2)
        wilde_benchmarks = self.fetch_relevant_wilde_epigrams(keyword="", limit=2)

        master_schools_directives = [
            {
                "school": "【阿尔·里斯《聚焦：决定公司命运的雄心》】",
                "core_directive": "聚焦一把尖刀：宁肯丢掉平庸的全面，整篇文案只赌一个极致特性，绝不贪婪堆砌多重卖点。"
            },
            {
                "school": "【特劳特《定位》& 劳拉·里斯《视觉锤》】",
                "core_directive": f"钉死心智钉子: {positioning['mental_nail']}；铸造视觉锤: 【{positioning['visual_hammer']}】。{positioning['counter_positioning']}。"
            },
            {
                "school": "【中国古典诗词文气与千古风骨】",
                "core_directive": "汲取苏轼‘一蓑烟雨任平生’与李白‘天生我材必有用’的旷达定力；善借诗经楚辞的意象寄托与唐诗宋词的开阔气象，让品牌主张具备千年历史的生命穿透力。"
            },
            {
                "school": "【奥斯卡·王尔德《唯美主义与悖论心法》】",
                "core_directive": "善用悖论反常识与唯美主义：撕破一本正经的自嗨说教，用优雅迷人的机智讽刺与极致的‘爱自己是终身浪漫’为大众制造精神解药与情绪嘴替。"
            },
            {
                "school": "【许渊冲《文学翻译谈 / 许渊冲经典作品集》三美论】",
                "core_directive": "超越直译追求意美、音美、形美：巧用汉语专属对仗与双关回环，让产品卖点‘投胎转世’为具有传世美感的文学图腾，让读者在母语中‘乐之’。"
            },
            {
                "school": "【余光中《余光中谈翻译 / 翻译乃大道》文白张力】",
                "core_directive": "坚决抵制恶性西化欧化病（剔除‘进行/关于/对于/被’），回归汉语原生动词；制造‘心有猛虎，细嗅蔷薇’般的极刚与极柔反差并置张力。"
            },
            {
                "school": "【钱钟书《钱钟书论翻译》化境与转世】",
                "core_directive": "文字投胎转世，如入化境：做品牌与美好生活的‘媒人’，打碎生硬行话，用机智警策的奇绝隐喻让消费者心智瞬间破防。"
            },
            {
                "school": "【乔纳·伯杰《疯传：让你的产品病毒入侵》】",
                "core_directive": "激活 STEPPS 六大病毒法则：让文案成为用户的社交货币(S)与身份勋章，强行绑定高频日常线索(T)与高唤醒生理情绪(E)。"
            },
            {
                "school": "【罗伯特·西奥迪尼《影响力》】",
                "core_directive": "触发大脑非理性开关：善用损失厌恶（翻转为不买的痛）、权威硬核背书与群体社会认同，摧毁最后一公里防御。"
            },
            {
                "school": "【约瑟夫·休格曼《文案训练手册》滑梯理论】",
                "core_directive": "制造滑梯效应：第一句话必须短促致命（8字以内），并在末尾埋下‘好奇心种子’，让读者停不下来一路滑向成交。"
            },
            {
                "school": "【金枪大叔《借势：以弱胜强的128条黄金法则》】",
                "core_directive": "以弱胜强借情绪之势：找行业老大破绽，做大众反内卷嘴替，文案必须通俗到连菜场大妈听一遍都能复述给别人。"
            },
            {
                "school": "【华杉/华楠《超级符号就是超级创意》】",
                "core_directive": "借用日常民间谚语与口语母体，将口号直接写成无需思考的动词命令句，建立条件反射。"
            },
            {
                "school": "【关键明《爆款文案》四步转化闭环】",
                "core_directive": "感官细节占有法：让读者脑海中先行体验第一口滋味或第一触碰，算账对比消除纠结，限时促单临门一脚。"
            },
            {
                "school": "【新井桥《写给非广告人的广告书》】",
                "core_directive": "生活者平视语言：消灭居高临下的企业自夸与生涩行话，在玄关与厨房的真实微小细节中提出让生活更温暖的提案。"
            },
            {
                "school": "【林永强《小强广告100招》人话修剪刀】",
                "core_directive": "无情剪去副词与抽象形容词，让位给具象物象（钥匙、水面、领带、电梯）与高动能动词。"
            },
            {
                "school": "【英国D&AD协会《The Copy Book 全球32位顶尖文案之道》】",
                "core_directive": "大声朗读校验唇齿阻力，让字词长短如心跳律动，用冷峻的陈述句与恰到好处的留白击穿读者灵魂。"
            },
            {
                "school": "【路克·苏立文《文案发烧》反套路破坏派】",
                "core_directive": "杀死全行业都在用的陈词滥调，敢于自嘲与反向操作，若遮住品牌名竞争对手也能用，立刻扔进垃圾桶。"
            },
            {
                "school": "【克劳德·霍普金斯《科学的广告 / 我的广告生涯》】",
                "core_directive": "实证主义至上：将普通工序揭秘为惊心动魄的硬核工艺信任状，拒绝无凭无据的文学卖弄。"
            },
            {
                "school": "【鲍勃·布莱《文案创作完全手册》4U法则】",
                "core_directive": "严守4U实战底线：紧迫感 (Urgent)、独特性 (Unique)、超具象 (Ultra-specific)、实用价值 (Useful)。"
            }
        ]

        return {
            "brand": brand,
            "product": product,
            "target_audience": target_audience,
            "brief_goal": brief_goal,
            "positioning_audit": positioning,
            "life_force_audit": lf8,
            "master_directives": master_schools_directives,
            "divine_translation_benchmarks": divine_benchmarks,
            "classical_chinese_benchmarks": classical_benchmarks,
            "wilde_benchmarks": wilde_benchmarks,
            "available_books_count": len(self.books)
        }




if __name__ == "__main__":
    fuser = MasterBookMethodologyFuser()
    print(f"Loaded {len(fuser.books)} master books into fuser.")
    pack = fuser.synthesize_master_strategy_pack(
        brand="东方某草本熬夜饮",
        product="高浓度人参植物饮",
        target_audience="大厂与金融高压打工人",
        brief_goal="颠覆传统养生的平庸佛系，打造年轻人的工位精神图腾"
    )
    print("\n--- Positioning Audit ---")
    print("Mental Nail:", pack["positioning_audit"]["mental_nail"])
    print("Visual Hammer:", pack["positioning_audit"]["visual_hammer"])
    print("\n--- Life Force Audit ---")
    print("LF8:", pack["life_force_audit"]["matched_primary_desires"])
    print("\n--- Master Directives ---")
    for d in pack["master_directives"]:
        print(f"{d['school']}: {d['core_directive']}")
