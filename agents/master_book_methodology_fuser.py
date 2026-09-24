#!/usr/bin/env python3
"""
master_book_methodology_fuser.py — Book Methodologies & Strategy Fusion Engine
Fuses principles from 18 classic copywriting & advertising books into generative heuristics:
  1. 特劳特《定位》/ 里斯《视觉锤》: 心智钉子 (Mental Nail) & 视觉锤 (Visual Hammer)
  2. 华与华《超级符号》: 文化母体寄生 & 超级行动指令
  3. 林桂枝《小强广告100招》: 文案修剪刀 (动词化、去副词、微感官)
  4. 德鲁·惠特曼《吸金广告》: LF8 生命原力映射
  5. 罗伯特·布莱《文案创作完全手册》: 4U 转化审计 (Urgent, Unique, Ultra-specific, Useful)
  6. 许舜英《意识形态》: 概念解构与先锋物哀美学
  7. 金鹏远《借势》: 社交货币与双关张力
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
    """Fuses 18 classic advertising book theories into generative strategy and copy heuristics."""

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

    def synthesize_master_strategy_pack(
        self,
        brand: str,
        product: str,
        target_audience: str,
        brief_goal: str
    ) -> Dict[str, Any]:
        """Synthesize masterclass strategic directives from all book methodologies."""
        combined_text = f"{brand} {product} {target_audience} {brief_goal}"
        positioning = self.craft_positioning_nail_and_hammer(brand, product, brief_goal)
        lf8 = self.map_life_force_8(combined_text)

        master_schools_directives = [
            {
                "school": "【特劳特定位与心智钉子派】",
                "core_directive": f"牢牢钉死心智钉子: {positioning['mental_nail']}，以【{positioning['visual_hammer']}】作为穿透媒介。"
            },
            {
                "school": "【华与华超级符号与购买指令派】",
                "core_directive": "借用日常民间谚语与口语母体，将文案直接写成无需思考的动词命令句，建立条件反射。"
            },
            {
                "school": "【林桂枝小强文案修剪派】",
                "core_directive": "坚决剔除任何公文词与副词，让形容词退场，让具体物象（钥匙、水面、领带、电梯）与动词发力。"
            },
            {
                "school": "【惠特曼吸金广告LF8生命原力派】",
                "core_directive": f"锁定原始生物本能: {lf8['matched_primary_desires'][0]}，先激活生存/焦虑痛感，再以产品为唯一安全解药。"
            },
            {
                "school": "【许舜英意识形态美学派】",
                "core_directive": "拒绝庸俗叫卖，将产品重构为当代人在平庸日常中对抗虚无的一把哲学钝器，沉淀高溢价文化资本。"
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
