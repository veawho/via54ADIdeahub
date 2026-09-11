#!/usr/bin/env python3
"""
test_mcp_tools.py — Test MCP tool endpoints directly
"""

import sys
import os
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mcp_server import (
    search_audience_language,
    reason_creative_strategy,
    search_knowledge_base,
    list_advertising_cases,
    get_kb_stats,
)

class TestMCPTools(unittest.TestCase):
    def test_search_audience_language_tool(self):
        # 1. Gay subculture
        res_str = search_audience_language(audience_type="gay", keyword="通关")
        data = json.loads(res_str)
        self.assertEqual(data["name"], "LGBT+ / Gay 圈层")
        self.assertTrue(data.get("keyword_match"))

        # 2. Patient subculture
        res_patient = search_audience_language(audience_type="patient")
        data_p = json.loads(res_patient)
        self.assertEqual(data_p["name"], "医疗健康与患者心声")

    def test_reason_creative_strategy_tool(self):
        res_str = reason_creative_strategy(
            brand="稳健先锋",
            product="男性长效防护制剂",
            target_audience="都市青年",
            brief_goal="建立安全、自洽、高端心智",
            audience_type="gay",
            version_count=5,
            emotion_check=True
        )
        data = json.loads(res_str)
        self.assertEqual(data["brand"], "稳健先锋")
        self.assertEqual(len(data["versions"]), 5)
        self.assertIn("markdown_card", data)
        self.assertIn("Critic 质检评分", data["markdown_card"])

    def test_kb_stats_and_cases(self):
        stats_str = get_kb_stats()
        stats = json.loads(stats_str)
        self.assertTrue(stats.get("kb_db_exists"))

        cases_str = list_advertising_cases(limit=5)
        cases = json.loads(cases_str)
        self.assertIn("total", cases)

if __name__ == "__main__":
    unittest.main()
