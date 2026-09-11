#!/usr/bin/env python3
"""
test_master_linguistic_engine.py — Tests for Masterclass 3-D Linguistic Engine
"""

import sys
import os
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.master_linguistic_engine import MasterLinguisticEngine
from mcp_server import analyze_linguistic_laws

class TestMasterLinguisticEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MasterLinguisticEngine()

    def test_pure_chinese_deconstruction(self):
        res = self.engine.deep_reverse_engineer("性别不是边界线，偏见才是")
        self.assertEqual(res["phonetic_dimension"]["language_mode"], "纯中文 (Pure Chinese)")
        self.assertIn("观念颠覆重构", res["semantic_dimension"]["tension_type"])
        self.assertGreaterEqual(res["overall_mastery_score"], 4.0)

    def test_bilingual_hybrid_deconstruction(self):
        res = self.engine.deep_reverse_engineer("你写PPT时，阿拉斯加的鳕鱼正跃出水面")
        self.assertEqual(res["phonetic_dimension"]["language_mode"], "中英文混合 (Bilingual Hybrid)")
        self.assertIn("PPT", res["phonetic_dimension"]["bilingual_harmony"])
        self.assertIn("极致张力撕扯", res["semantic_dimension"]["tension_type"])
        self.assertIn("具象画面物象", res["intuition_dimension"]["sensory_description"])
        self.assertGreaterEqual(res["overall_mastery_score"], 4.0)

    def test_evolved_slogans_synthesis(self):
        res = self.engine.evolve_master_slogans(
            reference_text="每一次尽兴的PLAY，都有不掉线的底气",
            brand="稳健伙伴",
            product="健康防线",
            target_audience="都市青年",
            audience_type="gay"
        )
        self.assertEqual(len(res["evolved_slogans"]), 5)
        for s in res["evolved_slogans"]:
            self.assertIn("headline", s)
            self.assertIn("mastery_score", s)
            self.assertGreaterEqual(s["mastery_score"], 3.5)
            self.assertIn("cadence_detail", s)
            self.assertIn("intuition_detail", s)

    def test_mcp_analyze_tool(self):
        res_str = analyze_linguistic_laws("Shot on iPhone, 记录真实生活")
        data = json.loads(res_str)
        self.assertEqual(data["phonetic_dimension"]["language_mode"], "中英文混合 (Bilingual Hybrid)")
        self.assertIn("iPhone", data["phonetic_dimension"]["bilingual_harmony"])

if __name__ == "__main__":
    unittest.main()
