#!/usr/bin/env python3
"""
test_phase2.py — Automated test suite for Phase 2 capabilities:
- New Subcultures (silver, pet, outdoor)
- CopyPolisher (diagnose, health score, compliance audit, 3 rewrites)
- PunEngine (phonetic pairing, cringe risk analysis)
- MCP Server Phase 2 tools
"""

import sys
import os
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.creative_reasoner import CreativeReasoner
from agents.pun_engine import PunEngine
from agents.copy_polisher import CopyPolisher
from mcp_server import (
    polish_and_diagnose_copy,
    explore_creative_puns,
    audit_advertising_compliance,
)

class TestPhase2Features(unittest.TestCase):
    def setUp(self):
        self.reasoner = CreativeReasoner()
        self.pun_engine = PunEngine()
        self.polisher = CopyPolisher()

    def test_new_subcultures(self):
        # Silver
        ctx_silver = self.reasoner.get_audience_context("silver")
        self.assertEqual(ctx_silver["name"], "银发经济与新老年活力")
        self.assertIn("第二人生", ctx_silver["core_keywords"])

        # Pet
        ctx_pet = self.reasoner.get_audience_context("pet")
        self.assertEqual(ctx_pet["name"], "养宠一族与毛孩子家长")
        self.assertIn("毛孩子", ctx_pet["core_keywords"])

        # Outdoor
        ctx_outdoor = self.reasoner.get_audience_context("outdoor")
        self.assertEqual(ctx_outdoor["name"], "山系青年与户外身心自救")
        self.assertIn("旷野", ctx_outdoor["core_keywords"])

    def test_pun_engine(self):
        res = self.pun_engine.generate_pun_concepts(
            brand="稳健伙伴",
            product="亲密防护制剂",
            core_benefit="全方位安全与从容自信",
            audience_type="gay"
        )
        self.assertEqual(res["brand"], "稳健伙伴")
        self.assertTrue(len(res["pun_proposals"]) >= 2)
        p1 = res["pun_proposals"][0]
        self.assertIn("surface_meaning", p1)
        self.assertIn("hidden_meaning", p1)
        self.assertIn("phonetic_pair", p1)
        self.assertIn("cringe_risk", p1)

    def test_copy_polisher_diagnosis(self):
        bad_copy = "非常优秀的第一品牌，你务必赶紧买，不要再执迷不悟，全面赋能你的生活，100%根治所有问题！"
        res = self.polisher.polish_copy(
            draft=bad_copy,
            target_audience="打工青年",
            brand="某元气饮",
            audience_type="genz"
        )
        diag = res["diagnosis"]
        self.assertLessEqual(diag["overall_health_score"], 2.0)
        self.assertTrue(len(diag["detected_preachy"]) > 0)
        self.assertTrue(len(diag["compliance_violations"]) > 0)
        self.assertEqual(len(res["polished_options"]), 3)

        card = self.polisher.render_polishing_card(res)
        self.assertIn("文案深度体检与重构诊断报告", card)
        self.assertIn("锐利脱水版", card)

    def test_compliance_audit_mcp(self):
        res_str = audit_advertising_compliance("我们是全国第一的顶级神效产品")
        res = json.loads(res_str)
        self.assertFalse(res["is_compliant"])
        self.assertGreaterEqual(res["violations_count"], 2)

    def test_polish_mcp_tool(self):
        res_str = polish_and_diagnose_copy(
            draft_text="退休了也要发挥余热，买这个给身体添动力",
            target_audience="退休中老年人",
            brand="银龄活力",
            audience_type="silver"
        )
        res = json.loads(res_str)
        self.assertEqual(res["audience_type"], "silver")
        self.assertIn("markdown_card", res)

    def test_pun_mcp_tool(self):
        res_str = explore_creative_puns(
            brand="山系之王",
            product="轻量化冲锋衣",
            core_benefit="防风防雨自由出行",
            audience_type="outdoor"
        )
        res = json.loads(res_str)
        self.assertIn("pun_proposals", res)

if __name__ == "__main__":
    unittest.main()
