#!/usr/bin/env python3
"""
integrations/feishu_bot_adapter.py — Feishu (Lark) Bot Unified Adapter for via54ADIdeahub
Bridges incoming Feishu messages/commands directly to the 3-D Linguistic Engine,
Creative Reasoner, Exemplar Reasoner, Copy Polisher, Pun Engine, and Brand Profiles.

Outputs native Feishu Card Markdown / Interactive Card JSON compliant with:
- 3-D Deep Reasoning (Sound + Meaning + Intuition)
- Mandatory >= 3 suggestions per request
- 4-D Similarity Benchmarks (读音/意义/表达/结构相似性)
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.master_linguistic_engine import MasterLinguisticEngine
from agents.creative_reasoner import CreativeReasoner
from agents.exemplar_reasoner import ExemplarReasoner
from agents.copy_polisher import CopyPolisher
from agents.pun_engine import PunEngine
from agents.brand_profile_manager import BrandProfileManager

class FeishuBotAdapter:
    """Unified Feishu Bot Adapter for via54ADIdeahub."""

    def __init__(self):
        self.linguistic_engine = MasterLinguisticEngine()
        self.creative_reasoner = CreativeReasoner()
        self.exemplar_reasoner = ExemplarReasoner()
        self.copy_polisher = CopyPolisher()
        self.pun_engine = PunEngine()
        self.brand_manager = BrandProfileManager()

    def handle_feishu_message(self, text: str, user_id: str = "", chat_id: str = "") -> Dict[str, Any]:
        """Dispatch incoming Feishu message to the optimal creative agent and return Feishu card markdown."""
        text_clean = text.strip()

        # 1. Intent: Exemplar Reverse-Engineering & Evolution
        # Keywords: 示例文案, 为什么好, 拆解文案, 逆向, 仿写, 参考文案, 为什么
        if any(k in text_clean for k in ["示例文案", "参考文案", "为什么好", "分析文案", "逆向", "拆解文案", "比这更好", "根据示例"]):
            exemplar_copy = self._extract_quoted_or_fallback(text_clean, default="自律给我自由")
            brand = self._extract_brand(text_clean, default="稳健先锋")
            res = self.exemplar_reasoner.evolve_beyond_exemplar(
                exemplar_copy=exemplar_copy,
                brand=brand,
                product="核心产品与服务",
                target_audience="目标受众",
                audience_type=self._detect_audience(text_clean)
            )
            card_md = self.exemplar_reasoner.render_evolution_card(res)
            return {
                "action": "exemplar_evolution",
                "card_markdown": card_md,
                "data": res
            }

        # 2. Intent: Copy Polishing & Diagnosis
        # Keywords: 诊断, 润色, 改写, 去爹味, 水词, 帮我改, 优化文案
        elif any(k in text_clean for k in ["诊断", "润色", "改写", "去爹味", "水词", "帮我改", "优化文案", "文案体检"]):
            draft = self._extract_quoted_or_fallback(text_clean, default="我们以极致卓越的科技赋能用户美好品质生活")
            brand = self._extract_brand(text_clean, default="品牌方")
            res = self.copy_polisher.polish_copy(
                draft=draft,
                target_audience="年轻受众",
                brand=brand,
                audience_type=self._detect_audience(text_clean)
            )
            card_md = self.copy_polisher.render_polishing_card(res)
            return {
                "action": "copy_polishing",
                "card_markdown": card_md,
                "data": res
            }

        # 3. Intent: Creative Pun & Double Entendre
        # Keywords: 双关, 谐音, 梗, 谐音梗
        elif any(k in text_clean for k in ["双关", "谐音", "梗", "谐音梗"]):
            brand = self._extract_brand(text_clean, default="创意品牌")
            res = self.pun_engine.generate_pun_concepts(
                brand=brand,
                product="核心产品",
                core_benefit="好喝清爽/舒适安心",
                audience_type=self._detect_audience(text_clean)
            )
            card_md = self.pun_engine.render_pun_card(res)
            return {
                "action": "creative_puns",
                "card_markdown": card_md,
                "data": res
            }

        # 4. Intent: Slogan Generation & Full Creative Strategy
        # Keywords: 口号, Slogan, 广告词, 策略, 写几个, 创意方案, 策划
        else:
            brand = self._extract_brand(text_clean, default="霸王茶姬")
            product = self._extract_product(text_clean, default="原叶现萃鲜奶茶")
            res = self.creative_reasoner.generate_creative_strategy(
                brand=brand,
                product=product,
                target_audience="都市新青年",
                brief_goal=text_clean,
                audience_type=self._detect_audience(text_clean),
                version_count=5,
                enable_critic=True
            )
            card_md = self.creative_reasoner.render_feishu_card(res)
            return {
                "action": "creative_strategy",
                "card_markdown": card_md,
                "data": res
            }

    def _extract_quoted_or_fallback(self, text: str, default: str) -> str:
        """Extract text within quotes or fallback."""
        m = re.search(r'["“「](.+?)["”」]', text)
        if m:
            return m.group(1).strip()
        # Fallback to text after keyword
        for kw in ["示例文案", "参考", "文案", "改改"]:
            if kw in text:
                parts = text.split(kw, 1)
                if len(parts) > 1 and len(parts[1].strip()) > 2:
                    return parts[1].strip(" :：，,")
        return default

    def _extract_brand(self, text: str, default: str) -> str:
        """Extract brand name from text."""
        for b in ["霸王茶姬", "Apple", "Keep", "珀莱雅", "稳健先锋", "稳健伙伴", "内外", "诚品", "杜蕾斯", "Nike", "OPPO"]:
            if b.lower() in text.lower():
                return b
        return default

    def _extract_product(self, text: str, default: str) -> str:
        """Extract product keyword from text."""
        for p in ["鲜奶茶", "防护", "健身", "美妆", "跑鞋", "手机", "书籍"]:
            if p in text:
                return p
        return default

    def _detect_audience(self, text: str) -> str:
        """Detect subculture audience from text."""
        if any(w in text for w in ["gay", "同志", "彩虹", "基友"]):
            return "gay"
        if any(w in text for w in ["00后", "打工人", "发疯", "去班味", "职场"]):
            return "genz"
        if any(w in text for w in ["女性", "女孩", "母婴", "闺蜜"]):
            return "women"
        if any(w in text for w in ["患者", "慢病", "健康", "药"]):
            return "patient"
        if any(w in text for w in ["老年", "银发", "爸妈", "退休"]):
            return "silver"
        if any(w in text for w in ["猫", "狗", "宠物", "毛孩子"]):
            return "pet"
        if any(w in text for w in ["户外", "徒步", "露营", "山系"]):
            return "outdoor"
        return "default"

if __name__ == "__main__":
    adapter = FeishuBotAdapter()
    test_queries = [
        "示例文案‘白天替体面演戏，夜晚让身体稳住’，帮我深度分析好在哪，并给出3个超越它的新口号",
        "帮霸王茶姬写5个新中式口号，要求符合声律且直击直觉",
        "帮我诊断并润色文案：‘我们以极致卓越的科技赋能用户美好品质生活’"
    ]
    for q in test_queries:
        print(f"\n====================\n💬 Feishu User: {q}\n====================")
        res = adapter.handle_feishu_message(q)
        print(f"🤖 Bot Action: {res['action']}")
        print(f"📄 Feishu Card Markdown Snippet:\n{res['card_markdown'][:400]}...\n")
