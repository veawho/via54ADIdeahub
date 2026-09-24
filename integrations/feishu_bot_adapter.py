#!/usr/bin/env python3
"""
integrations/feishu_bot_adapter.py — Feishu (Lark) Bot Unified Adapter for via54ADIdeahub
Bridges incoming Feishu messages/commands directly to:
  1. Creative Reasoner (Full Creative Strategy with Ping-Ze, Self-Refine & Psycholinguistics)
  2. Copywriting Mastery Auditor (Phonetics, Literary Genre, Cognitive Tension, Master Books, Dehydration, Neuro-Activation)
  3. Exemplar Reasoner (3-D Reverse-Engineering of Exemplars with 5 Superior Evolutions)
  4. Copy Polisher (De-Fluffing & Anti-Patronizing Upgrade with 3 Reconstructed Options)
  5. Pun Engine (Double Entendre & Social Memes)
  6. Brand Profile Manager

Outputs:
  - Native Feishu Card Markdown
  - Native Feishu Interactive Card JSON (Open Platform compatible)
  - Direct Webhook Pushing Utility
"""

import sys
import os
import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.master_linguistic_engine import MasterLinguisticEngine
from agents.creative_reasoner import CreativeReasoner
from agents.exemplar_reasoner import ExemplarReasoner
from agents.copy_polisher import CopyPolisher
from agents.pun_engine import PunEngine
from agents.brand_profile_manager import BrandProfileManager
from agents.copywriting_art_auditor import CopywritingMasteryAuditor
from agents.psycholinguistic_activator import PsycholinguisticActivator


BRAND_STOP_WORDS = {
    "我们", "自己", "大家", "需要", "产出", "一句", "几个", "并给", "帮我", "给我", "请帮",
    "设计", "策划", "生成", "制作", "这个", "那个", "某个", "一个", "示例", "参考", "文案",
    "口号", "品牌", "公司", "分析", "好在", "哪儿", "哪里", "超越", "诊断", "润色", "改写",
    "体检", "审计", "打分", "评估", "脱水", "新式", "现代", "优质", "核心", "可以", "如何",
    "要求", "符合", "直击", "直觉", "声律", "平仄", "十三辙", "神仙", "翻译", "古诗"
}

KNOWN_BRANDS = [
    "霸王茶姬", "茶颜悦色", "喜茶", "奈雪的茶", "奈雪", "Apple", "苹果",
    "Keep", "珀莱雅", "欧莱雅", "雅诗兰黛", "资生堂", "稳健先锋", "稳健伙伴",
    "内外", "诚品", "诚品书店", "杜蕾斯", "Nike", "耐克", "Adidas", "阿迪达斯",
    "OPPO", "vivo", "华为", "小米", "东方草本", "蕉内", "观夏", "闻献",
    "胖东来", "海底捞", "农夫山泉", "元气森林", "三顿半", "瑞幸", "星巴克",
    "蕉下", "Lululemon", "始祖鸟", "Salomon", "安踏", "李宁"
]


class FeishuBotAdapter:
    """Unified Feishu Bot Adapter for via54ADIdeahub."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (PROJECT_ROOT / "via54_kb.db")
        self.linguistic_engine = MasterLinguisticEngine()
        self.creative_reasoner = CreativeReasoner(self.db_path)
        self.exemplar_reasoner = ExemplarReasoner(self.db_path)
        self.copy_polisher = CopyPolisher(self.db_path)
        self.pun_engine = PunEngine()
        self.brand_manager = BrandProfileManager()
        self.mastery_auditor = CopywritingMasteryAuditor(self.db_path)
        self.psycholinguistic_activator = PsycholinguisticActivator(self.db_path)

    def handle_feishu_message(self, text: str, user_id: str = "", chat_id: str = "") -> Dict[str, Any]:
        """Dispatch incoming Feishu message to the optimal creative agent and return Feishu card markdown + interactive JSON."""
        text_clean = text.strip()

        # Classify intent with high-precision priority resolution
        intent = self._classify_intent(text_clean)

        # ── 1. Intent: Copy Polishing & Diagnosis (润色 / 去爹味 / 脱水) ────────
        if intent == "copy_polishing":
            draft = self._extract_quoted_or_fallback(
                text_clean,
                default="我们以极致卓越的科技赋能用户美好品质生活"
            )
            brand = self._extract_brand(text_clean, default="")
            res = self.copy_polisher.polish_copy(
                draft=draft,
                target_audience=self._extract_target_audience(text_clean),
                brand=brand,
                audience_type=self._detect_audience(text_clean)
            )
            card_md = self.copy_polisher.render_polishing_card(res)
            interactive_card = self.build_feishu_interactive_card(
                title=f"📝 文案全维体检诊断与三大重构升级 · {brand or '品牌'}",
                markdown_content=card_md,
                header_color="orange"
            )
            return {
                "action": "copy_polishing",
                "card_markdown": card_md,
                "interactive_card": interactive_card,
                "data": res
            }

        # ── 2. Intent: Exemplar Reverse-Engineering & Evolution (标杆逆向 / 拆解超越) ─
        elif intent == "exemplar_evolution":
            exemplar_copy = self._extract_quoted_or_fallback(
                text_clean,
                default="自律给我自由"
            )
            brand = self._extract_brand(text_clean, default="")
            product = self._extract_product(text_clean, brand=brand, default="核心产品与服务")
            audience = self._extract_target_audience(text_clean)
            audience_type = self._detect_audience(text_clean)

            res = self.exemplar_reasoner.evolve_beyond_exemplar(
                exemplar_copy=exemplar_copy,
                brand=brand,
                product=product,
                target_audience=audience,
                audience_type=audience_type
            )
            card_md = self.exemplar_reasoner.render_evolution_card(res)
            interactive_card = self.build_feishu_interactive_card(
                title=f"🧬 经典文案逆推与对标升维全案 · {brand or '标杆'}",
                markdown_content=card_md,
                header_color="turquoise"
            )
            return {
                "action": "exemplar_evolution",
                "card_markdown": card_md,
                "interactive_card": interactive_card,
                "data": res
            }

        # ── 3. Intent: Mastery Copywriting Audit (显式打分 / 声律体检 / 神经激活审计) ──
        elif intent == "mastery_audit":
            target_text = self._extract_quoted_or_fallback(
                text_clean,
                default="白天替体面演戏，夜晚还自己峥嵘"
            )
            brand = self._extract_brand(text_clean, default="")
            audit_res = self.mastery_auditor.audit_copywriting(target_text, brand=brand)
            card_md = self.mastery_auditor.render_markdown_report(audit_res)
            interactive_card = self.build_feishu_interactive_card(
                title=f"🏛️ 【{brand or '文案'}】全维艺术与神经激活审计报告",
                markdown_content=card_md,
                header_color="carmine" if audit_res["composite_mastery_score"] < 70 else "blue"
            )
            return {
                "action": "mastery_audit",
                "card_markdown": card_md,
                "interactive_card": interactive_card,
                "data": audit_res
            }

        # ── 4. Intent: Creative Pun & Double Entendre (谐音双关) ─────────────
        elif intent == "creative_puns":
            brand = self._extract_brand(text_clean, default="创意品牌")
            product = self._extract_product(text_clean, brand=brand, default="核心产品")
            res = self.pun_engine.generate_pun_concepts(
                brand=brand,
                product=product,
                core_benefit="好喝清爽/舒适安心",
                audience_type=self._detect_audience(text_clean)
            )
            card_md = self.pun_engine.render_pun_card(res)
            interactive_card = self.build_feishu_interactive_card(
                title=f"🎭 精品双关与社交裂变梗 · {brand}",
                markdown_content=card_md,
                header_color="yellow"
            )
            return {
                "action": "creative_puns",
                "card_markdown": card_md,
                "interactive_card": interactive_card,
                "data": res
            }

        # ── 5. Intent: Full Creative Campaign Strategy & Slogans Matrix (Default) ──
        else:
            brand = self._extract_brand(text_clean, default="")
            product = self._extract_product(text_clean, brand=brand, default="核心产品与服务")
            target_audience = self._extract_target_audience(text_clean)
            audience_type = self._detect_audience(text_clean)
            version_count = self._extract_version_count(text_clean, default=5)

            res = self.creative_reasoner.generate_creative_strategy(
                brand=brand,
                product=product,
                target_audience=target_audience,
                brief_goal=text_clean,
                audience_type=audience_type,
                version_count=version_count,
                enable_critic=True
            )
            card_md = self.creative_reasoner.render_feishu_card(res)
            interactive_card = self.build_feishu_interactive_card(
                title=f"🌌 【{res['brand']}】创意品牌全案与口号矩阵",
                markdown_content=card_md,
                header_color="blue"
            )
            return {
                "action": "creative_strategy",
                "card_markdown": card_md,
                "interactive_card": interactive_card,
                "data": res
            }

    def _classify_intent(self, text: str) -> str:
        """Accurately classify user intent, strictly preventing generation requests from being hijacked by audit."""
        # 1. Check for explicit copy polishing/rewriting keywords
        polishing_keywords = ["润色", "去爹味", "水词", "改写", "帮我改", "改改", "优化文案", "脱水", "删减水词", "文案润色", "文案诊断"]
        if any(k in text for k in polishing_keywords):
            return "copy_polishing"

        # 2. Check for exemplar reverse-engineering
        exemplar_keywords = ["示例文案", "参考文案", "为什么好", "好在哪", "拆解文案", "文案拆解", "逆向", "超越示例", "标杆逆向", "对标示例", "根据示例", "比这更好"]
        if any(k in text for k in exemplar_keywords):
            return "exemplar_evolution"

        # 3. Check for creative puns / memes
        pun_keywords = ["双关", "谐音梗", "谐音双关", "出个梗", "谐音"]
        if any(k in text for k in pun_keywords) and not any(k in text for k in ["全案", "矩阵", "品牌主张", "宣言"]):
            return "creative_puns"

        # 4. Check for pure audit intent:
        # User wants to audit/inspect/score an existing copy, AND NOT ask to generate/create new ones.
        has_generation_verbs = any(v in text for v in [
            "写", "策划", "创作", "生成", "创想", "想几个", "来几个", "出几个", "做几个", "设计", "打造", "定制",
            "口号", "slogan", "Slogan", "全案", "主张"
        ])

        audit_prefix = text.startswith(("审计", "全维审计", "文案审计", "评分", "打分", "评估", "文案体检", "检查平仄", "检查声律", "质检"))
        has_audit_keywords = any(k in text for k in ["审计", "文案审计", "文案打分", "文案评分", "检查平仄", "平仄检查", "检查声律", "声律检查", "文案质检"])

        if audit_prefix or (has_audit_keywords and not has_generation_verbs):
            return "mastery_audit"

        # 5. Default to creative strategy generation
        return "creative_strategy"

    def build_feishu_interactive_card(
        self,
        title: str,
        markdown_content: str,
        header_color: str = "blue"
    ) -> Dict[str, Any]:
        """Construct standard Feishu Open Platform Interactive Card payload."""
        return {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True,
                    "enable_forward": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title[:60]
                    },
                    "template": header_color
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": markdown_content
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "content": "⚡ 由 via54ADIdeahub 认知神经与汉语言艺术中枢智能驱动"
                            }
                        ]
                    }
                ]
            }
        }

    def send_to_webhook(self, webhook_url: str, card_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Post card payload directly to a Feishu custom robot webhook URL."""
        if not webhook_url:
            return {"error": "Missing webhook_url"}

        try:
            req_data = json.dumps(card_payload).encode("utf-8")
            req = urllib.request.Request(
                webhook_url,
                data=req_data,
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                resp_text = response.read().decode("utf-8")
                return json.loads(resp_text)
        except Exception as e:
            return {"error": f"Failed to push to Feishu webhook: {str(e)}"}

    def _extract_quoted_or_fallback(self, text: str, default: str) -> str:
        """Extract text within quotes or fallback after keywords with clean clause truncation."""
        # 1. Match paired quotes: “”, 「」, ‘’, '', "", 『』
        m = re.search(r'["“「‘\'\`『](.+?)["”」’\'\`』]', text)
        if m:
            extracted = m.group(1).strip()
            if len(extracted) >= 2:
                return extracted

        # 2. Extract content following common cue prefixes
        cue_keywords = [
            "示例文案", "参考文案", "文案体检", "体检文案", "诊断文案",
            "润色文案", "审计文案", "文案审计", "比如", "这句文案", "文案", "改改"
        ]
        for kw in cue_keywords:
            if kw in text:
                parts = text.split(kw, 1)
                if len(parts) > 1 and len(parts[1].strip()) >= 2:
                    val = parts[1].strip(" :：，,")
                    # Truncate follow-up prompt instructions
                    val = re.split(r'[，,。；;\n]\s*(?:帮我|并给出|要求|请|分析|好在哪|为什么|超越|为|给|针对|写出)', val)[0].strip()
                    val = val.strip("“\"'‘「」’”`『』")
                    if len(val) >= 2:
                        return val

        return default

    def _extract_brand(self, text: str, default: str = "") -> str:
        """Extract brand name dynamically with dictionary lookup, explicit markers, and stopword sanitization."""
        # 1. Known brand dictionary priority match
        for b in KNOWN_BRANDS:
            if b.lower() in text.lower():
                return b

        # 2. Explicit Brand Markers: 品牌：xxx / 品牌为xxx / 【xxx】
        m_explicit = re.search(r'(?:品牌[：:]|品牌为|品牌是)\s*([A-Za-z0-9\u4e00-\u9fff]{2,10})', text)
        if m_explicit:
            cand = m_explicit.group(1).strip()
            if cand not in BRAND_STOP_WORDS:
                return cand

        m_bracket = re.search(r'【([A-Za-z0-9\u4e00-\u9fff]{2,10})】', text)
        if m_bracket:
            cand = m_bracket.group(1).strip()
            if cand not in BRAND_STOP_WORDS:
                return cand

        # 3. Preposition-based extraction (Preposition is strictly required)
        m = re.search(r'(?:为|帮|给|针对|服务于)\s*([A-Za-z0-9\u4e00-\u9fff]{2,10}?)(?:品牌|公司)?\s*(?:写|策划|出|做|设计|生成|打造|定制|量身)', text)
        if m:
            cand = m.group(1).strip()
            if cand not in BRAND_STOP_WORDS and len(cand) >= 2:
                return cand

        # 4. Fallback inference from domain keywords
        if any(k in text for k in ["茶", "奶茶", "原叶", "鲜奶茶"]):
            return "新中式东方茶饮"
        if any(k in text for k in ["减重", "脂肪肝", "减脂", "轻盈", "肥胖", "代谢"]):
            return "健康减重品牌"
        if any(k in text for k in ["抗老", "早C晚A", "护肤", "美白", "精华"]):
            return "先锋护肤科技品牌"
        if any(k in text for k in ["健身", "运动", "跑鞋", "撸铁", "自律"]):
            return "运动健康先锋"

        return default

    def _extract_product(self, text: str, brand: str = "", default: str = "核心产品与服务") -> str:
        """Extract product keyword from text or brand context."""
        product_mappings = [
            (["鲜奶茶", "原叶茶", "奶茶", "拿铁", "茶饮"], "原叶鲜奶茶与东方茶饮"),
            (["早C晚A", "精华", "抗衰", "面霜", "美妆", "防晒", "护肤"], "先锋科技护肤与抗衰精华"),
            (["减重", "脂肪肝", "减脂", "轻盈", "代谢", "肝脏"], "减重与肝脏健康管理产品"),
            (["跑鞋", "运动服", "健身", "智能手环", "动感单车"], "运动科技与专业健身装备"),
            (["防晒衣", "凉感", "遮阳", "伞"], "轻量化防晒与户外服饰"),
            (["手机", "平板", "电脑", "耳机", "手表"], "消费级前沿科技硬件与生态"),
            (["咖啡", "挂耳", "冷萃", "浓缩"], "精品原产地现磨与冷萃咖啡"),
            (["书籍", "阅读", "出版", "书店"], "人文精神读物与文化出版物"),
            (["香氛", "香水", "香薰"], "东方气味与当代情绪香氛"),
        ]
        for keywords, prod_name in product_mappings:
            if any(k in text for k in keywords):
                return prod_name

        brand_defaults = {
            "霸王茶姬": "原叶鲜奶茶与东方茶饮",
            "茶颜悦色": "新式国风鲜茶饮",
            "喜茶": "新茶饮与灵感之茶",
            "Keep": "智能健身与运动健康管理",
            "珀莱雅": "先锋科技护肤与早C晚A抗衰精华",
            "Apple": "消费级前沿科技硬件与智能生态",
            "杜蕾斯": "安全亲密关系与情感守护产品",
            "诚品": "人文生活阅读与文化生活空间",
            "内外": "舒适内衣与身心探索生活方式",
            "蕉内": "体感科技生活服装与内着",
            "蕉下": "轻量化户外与防晒装备"
        }
        if brand in brand_defaults:
            return brand_defaults[brand]

        return default

    def _extract_target_audience(self, text: str) -> str:
        """Extract target audience description."""
        if any(k in text for k in ["脂肪肝", "减重", "肥胖", "代谢"]):
            return "脂肪肝与减重患者群体"
        if any(k in text for k in ["00后", "打工人", "职场", "新青年"]):
            return "年轻打工人与新职场青年"
        if any(k in text for k in ["女性", "女孩", "母婴", "职场女性"]):
            return "现代独立女性群体"
        if any(k in text for k in ["同志", "彩虹", "基友", "gay"]):
            return "多元包容同志社群"
        if any(k in text for k in ["老年", "银发", "爸妈", "退休"]):
            return "银发长者与品质退休群体"
        return "都市主流目标客群"

    def _detect_audience(self, text: str) -> str:
        """Detect subculture audience identifier."""
        if any(w in text for w in ["脂肪肝", "减重", "患者", "慢病", "健康", "药", "病"]):
            return "patient"
        if any(w in text for w in ["gay", "同志", "彩虹", "基友"]):
            return "gay"
        if any(w in text for w in ["00后", "打工人", "发疯", "去班味", "职场"]):
            return "genz"
        if any(w in text for w in ["女性", "女孩", "母婴", "闺蜜"]):
            return "women"
        if any(w in text for w in ["老年", "银发", "爸妈", "退休"]):
            return "silver"
        if any(w in text for w in ["猫", "狗", "宠物", "毛孩子"]):
            return "pet"
        if any(w in text for w in ["户外", "徒步", "露营", "山系"]):
            return "outdoor"
        return "default"

    def _extract_version_count(self, text: str, default: int = 5) -> int:
        """Extract requested version count (capped between 1 and 5)."""
        m = re.search(r'([1-5])\s*个(?:口号|版本|方案|主张|Slogan)?', text)
        if m:
            return int(m.group(1))
        return default


if __name__ == "__main__":
    adapter = FeishuBotAdapter()
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"🤖 Processing Feishu Message: {query}")
        out = adapter.handle_feishu_message(query)
        print(f"Action: {out['action']}")
        print(out["card_markdown"])
    else:
        test_queries = [
            "审计文案：‘我们致力于全面赋能每一个用户的优质健康生活’",
            "帮霸王茶姬写5个新中式口号，要求符合声律且直击直觉",
            "帮我诊断并润色文案：‘我们以极致卓越的科技赋能用户美好品质生活’",
            "‘白天替体面演戏，夜晚让身体稳住’，分析这句文案为什么好，并为珀莱雅写3个超越它的新口号"
        ]
        for q in test_queries:
            print(f"\n====================\n💬 Feishu User: {q}\n====================")
            res = adapter.handle_feishu_message(q)
            print(f"🤖 Bot Action: {res['action']}")
            print(f"📄 Card Markdown Snippet:\n{res['card_markdown'][:400]}...\n")
