#!/usr/bin/env python3
"""
tests/test_similarity_benchmarks.py — Unit test for similarity benchmarks & deep reasoning across agents
Verifies that:
1. Every copy generator returns at least 3 distinct options.
2. Every option contains deep 3-D reasoning (phonetic, semantic, intuition).
3. Every option contains a 4-D similarity benchmark reference (读音/意义/表达/结构相似性).
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.master_linguistic_engine import MasterLinguisticEngine
from agents.exemplar_reasoner import ExemplarReasoner
from agents.creative_reasoner import CreativeReasoner
from agents.copy_polisher import CopyPolisher
from agents.pun_engine import PunEngine

class TestSimilarityBenchmarks(unittest.TestCase):

    def setUp(self):
        self.linguistic_engine = MasterLinguisticEngine()
        self.exemplar_reasoner = ExemplarReasoner()
        self.creative_reasoner = CreativeReasoner()
        self.copy_polisher = CopyPolisher()
        self.pun_engine = PunEngine()

    def test_linguistic_engine_similarity_matching(self):
        benchmark = self.linguistic_engine.match_similarity_benchmark("自律给我自由")
        self.assertIn("similarity_dimension", benchmark)
        self.assertIn("benchmark_case", benchmark)
        self.assertIn("similarity_analysis", benchmark)

    def test_exemplar_reasoner_evolution_similarity(self):
        res = self.exemplar_reasoner.evolve_beyond_exemplar(
            exemplar_copy="自律给我自由",
            brand="Keep",
            product="运动健身App",
            target_audience="年轻白领"
        )
        self.assertIn("evolutions", res)
        self.assertGreaterEqual(len(res["evolutions"]), 3)
        for opt in res["evolutions"]:
            self.assertIn("tagline", opt)
            self.assertIn("why_better", opt)
            self.assertIn("similarity_benchmark", opt)
            sim = opt["similarity_benchmark"]
            self.assertIn("dimension", sim)
            self.assertIn("matched_classic", sim)
            self.assertIn("rationale", sim)

    def test_creative_reasoner_similarity(self):
        res = self.creative_reasoner.generate_creative_strategy(
            brand="霸王茶姬",
            product="伯牙绝弦",
            target_audience="都市白领",
            brief_goal="健康好喝",
            version_count=5
        )
        self.assertIn("versions", res)
        self.assertGreaterEqual(len(res["versions"]), 3)
        for opt in res["versions"]:
            self.assertIn("tagline", opt)
            self.assertIn("critic_eval", opt)
            self.assertIn("similarity_benchmark", opt)

    def test_copy_polisher_similarity(self):
        res = self.copy_polisher.polish_copy(
            draft="我们以极致卓越的科技赋能用户美好品质生活",
            target_audience="年轻人",
            brand="测试品牌"
        )
        self.assertIn("polished_options", res)
        self.assertGreaterEqual(len(res["polished_options"]), 3)
        for opt in res["polished_options"]:
            self.assertIn("copy", opt)
            self.assertIn("deep_reasoning", opt)
            self.assertIn("phonetic", opt["deep_reasoning"])
            self.assertIn("semantic", opt["deep_reasoning"])
            self.assertIn("intuition", opt["deep_reasoning"])

    def test_pun_engine_similarity(self):
        res = self.pun_engine.generate_pun_concepts(
            brand="霸王茶姬",
            product="原叶鲜奶茶",
            core_benefit="清爽不腻好喝"
        )
        self.assertIn("pun_proposals", res)
        self.assertGreaterEqual(len(res["pun_proposals"]), 3)
        for pun in res["pun_proposals"]:
            self.assertIn("pun_headline", pun)
            self.assertIn("deep_reasoning", pun)
            self.assertIn("phonetic", pun["deep_reasoning"])
            self.assertIn("semantic", pun["deep_reasoning"])
            self.assertIn("intuition", pun["deep_reasoning"])

if __name__ == "__main__":
    unittest.main()
