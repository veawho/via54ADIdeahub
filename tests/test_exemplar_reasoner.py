#!/usr/bin/env python3
"""
test_exemplar_reasoner.py — Automated tests for Exemplar Reverse-Engineering & Linguistic Evolution
"""

import sys
import os
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.exemplar_reasoner import ExemplarReasoner
from mcp_server import deconstruct_and_evolve_copy

class TestExemplarReasoner(unittest.TestCase):
    def setUp(self):
        self.engine = ExemplarReasoner()

    def test_phonetic_cadence_audit(self):
        res1 = self.engine.audit_phonetic_cadence("稳住全场，从容通关")
        self.assertGreaterEqual(res1["cadence_score"], 4.5)
        self.assertEqual(res1["rhythm_pattern"], "4+4")
        self.assertIn("4+4", res1["symmetry_description"])

        res2 = self.engine.audit_phonetic_cadence("白天替体面演戏，夜晚让身体稳住")
        self.assertEqual(res2["rhythm_pattern"], "7+7")
        self.assertIn("7+7", res2["symmetry_description"])

    def test_deconstruct_exemplar(self):
        dec = self.engine.deconstruct_exemplar(
            exemplar_copy="性别不是边界线，偏见才是",
            target_audience="独立女性",
            audience_type="women"
        )
        self.assertIn("观念颠覆重构", dec["semantic_dimension"]["tension_type"])
        self.assertIn("core_law_summary", dec)

    def test_evolve_beyond_exemplar(self):
        res = self.engine.evolve_beyond_exemplar(
            exemplar_copy="白天替体面演戏，夜晚让身体稳住",
            brand="稳健先锋",
            product="男性长效防护制剂",
            target_audience="都市新中产",
            audience_type="gay"
        )
        self.assertEqual(res["brand"], "稳健先锋")
        self.assertEqual(len(res["evolutions"]), 5)
        
        for ev in res["evolutions"]:
            self.assertIn("archetype", ev)
            self.assertIn("why_better", ev)
            self.assertTrue(len(ev["why_better"]) > 10)
            self.assertIn("cadence_eval", ev)

        card = self.engine.render_evolution_card(res)
        self.assertIn("经典文案三维底层规律深度逆推", card)
        self.assertIn("超越升维依据", card)

    def test_mcp_deconstruct_tool(self):
        res_str = deconstruct_and_evolve_copy(
            exemplar_copy="在书与非书之间，我们阅读生活",
            brand="诚品生活",
            product="文化生活空间",
            target_audience="文艺青年",
            audience_type="genz"
        )
        data = json.loads(res_str)
        self.assertIn("deconstruction", data)
        self.assertIn("evolutions", data)
        self.assertIn("markdown_card", data)

if __name__ == "__main__":
    unittest.main()
