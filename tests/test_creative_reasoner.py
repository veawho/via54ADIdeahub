#!/usr/bin/env python3
"""
test_creative_reasoner.py — Standard library unittest for CreativeReasoner & Audience Language
"""

import sys
import os
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.creative_reasoner import CreativeReasoner
from tools.pun_db_builder import get_pun_cases

class TestCreativeReasonerUpgrade(unittest.TestCase):
    def setUp(self):
        self.reasoner = CreativeReasoner()

    def test_audience_context_loading(self):
        gay_ctx = self.reasoner.get_audience_context("gay")
        self.assertEqual(gay_ctx["name"], "LGBT+ / Gay 圈层")
        self.assertIn("通关", gay_ctx["core_keywords"])
        self.assertIn("去悲情化", gay_ctx["guidelines_markdown"])

        genz_ctx = self.reasoner.get_audience_context("genz")
        self.assertIn("去班味", genz_ctx["core_keywords"])
        self.assertTrue(len(genz_ctx["guidelines_markdown"]) > 50)

        patient_ctx = self.reasoner.get_audience_context("patient")
        self.assertIn("大白话洞察", patient_ctx["tags"])

    def test_pun_database(self):
        pun_cases = get_pun_cases(limit=5)
        self.assertTrue(len(pun_cases) > 0)
        first = pun_cases[0]
        self.assertIn("brand", first)
        self.assertIn("pun_text", first)
        self.assertGreaterEqual(first["quality_score"], 4.0)

    def test_creative_strategy_5_versions(self):
        res = self.reasoner.generate_creative_strategy(
            brand="灵犀",
            product="年轻态草本养生饮",
            target_audience="大厂高压00后",
            brief_goal="让养生变得像喝奶茶一样潮和解压",
            audience_type="genz",
            version_count=5,
            enable_critic=True
        )
        
        self.assertEqual(res["brand"], "灵犀")
        self.assertEqual(res["audience_type"], "genz")
        self.assertEqual(len(res["versions"]), 5)
        
        categories = [v["style_category"] for v in res["versions"]]
        self.assertTrue(any("反转热梗型" in c for c in categories))
        self.assertTrue(any("情绪嘴替型" in c for c in categories))
        self.assertTrue(any("故事叙事型" in c for c in categories))
        self.assertTrue(any("数据背书型" in c for c in categories))
        self.assertTrue(any("圈层共鸣型" in c for c in categories))
        
        for v in res["versions"]:
            eval_data = v["critic_eval"]
            self.assertIn("emotion_score", eval_data)
            self.assertTrue(1.0 <= eval_data["emotion_score"] <= 5.0)
            self.assertIn("humanity_score", eval_data)
            self.assertIn("critic_feedback", eval_data)

    def test_water_word_audit(self):
        bad_text = "非常优秀的产品，真正做到极其震撼，不得不说十分令人感动"
        audit = self.reasoner.audit_water_words(bad_text)
        self.assertFalse(audit["is_clean"])
        self.assertGreaterEqual(len(audit["detected_water_words"]), 3)
        
        clean_text = "白天替体面演戏，夜晚让身体稳住"
        audit_clean = self.reasoner.audit_water_words(clean_text)
        self.assertTrue(audit_clean["is_clean"])

    def test_feishu_rendering(self):
        res = self.reasoner.generate_creative_strategy(
            brand="测试品牌",
            product="测试产品",
            target_audience="测试客群",
            brief_goal="测试目标",
            audience_type="patient",
            version_count=3
        )
        card_md = self.reasoner.render_feishu_card(res)
        self.assertIn("# 🌌 【测试品牌】", card_md)
        self.assertIn("Critic 质检评分", card_md)
        self.assertIn("版本 1", card_md)

if __name__ == "__main__":
    unittest.main()
