#!/usr/bin/env python3
"""
scripts/mcp_health_check.py — MCP Server End-to-End Health Check
Tests all MCP tool implementations directly and verifies responses.
"""

import sys
import os
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import mcp_server

def run_health_check():
    print("==================================================")
    print("🚀 Running via54ADIdeahub MCP Server Health Check")
    print("==================================================")
    
    passed = 0
    total = 0

    def test_tool(name, func, *args, **kwargs):
        nonlocal passed, total
        total += 1
        print(f"\n[{total}] Testing '{name}'...")
        try:
            res_str = func(*args, **kwargs)
            res = json.loads(res_str)
            if "error" in res:
                print(f"❌ '{name}' returned error: {res['error']}")
                return False
            print(f"✅ '{name}' passed.")
            passed += 1
            return True
        except Exception as e:
            print(f"❌ '{name}' exception: {e}")
            return False

    # 1. get_kb_stats
    test_tool("get_kb_stats", mcp_server.get_kb_stats)

    # 2. search_knowledge_base
    test_tool("search_knowledge_base", mcp_server.search_knowledge_base, query="霸王茶姬", top_k=2)

    # 3. list_advertising_cases
    test_tool("list_advertising_cases", mcp_server.list_advertising_cases, limit=5)

    # 4. get_case_detail
    test_tool("get_case_detail", mcp_server.get_case_detail, industry="Food_Beverage", brand="Chagee", case_name="Chagee_2024")

    # 5. search_audience_language
    test_tool("search_audience_language", mcp_server.search_audience_language, audience_type="gay", keyword="出柜")

    # 6. reason_creative_strategy
    test_tool("reason_creative_strategy", mcp_server.reason_creative_strategy,
              brand="霸王茶姬", product="伯牙绝弦原叶鲜奶茶", target_audience="都市白领", brief_goal="强调真茶真奶天然健康")

    # 7. polish_and_diagnose_copy
    test_tool("polish_and_diagnose_copy", mcp_server.polish_and_diagnose_copy,
              draft_text="我们以极致卓越的科技赋能用户美好品质生活", target_audience="00后年轻人")

    # 8. explore_creative_puns
    test_tool("explore_creative_puns", mcp_server.explore_creative_puns,
              brand="霸王茶姬", product="原叶鲜奶茶", core_benefit="清爽不腻好喝")

    # 9. audit_advertising_compliance
    test_tool("audit_advertising_compliance", mcp_server.audit_advertising_compliance,
              text="这是全网第一、最顶级的天然好茶")

    # 10. deconstruct_and_evolve_copy
    test_tool("deconstruct_and_evolve_copy", mcp_server.deconstruct_and_evolve_copy,
              exemplar_copy="自律给我自由", brand="Keep", product="运动健身App", target_audience="年轻白领")

    # 11. analyze_linguistic_laws
    test_tool("analyze_linguistic_laws", mcp_server.analyze_linguistic_laws,
              copy_text="喝茶就要 PLAY，赢要 WIN 得痛快")

    # 12. manage_brand_profiles
    test_tool("manage_brand_profiles (list)", mcp_server.manage_brand_profiles, action="list")
    test_tool("manage_brand_profiles (get)", mcp_server.manage_brand_profiles, action="get", brand_id="apple")

    print("\n==================================================")
    print(f"🎯 Health Check Result: {passed}/{total} tools passed.")
    print("==================================================")
    return passed == total

if __name__ == "__main__":
    success = run_health_check()
    sys.exit(0 if success else 1)
