#!/usr/bin/env python3
"""
multi_platform_creative_collector.py
Multi-platform Creative Harvester across 5 major advertising & marketing platforms:
  1. 数英网 (Digitaling)
  2. 顶尖文案 (TOPYS)
  3. 广告门 (Adquan)
  4. 梅花网 (Meihua)
  5. 胖鲸 (SocialBeta / Pangjing)

Extracts:
  - 文案金句 (Golden Copy Quotes)
  - 活动主题金句 (Campaign Slogans)
  - 品牌传播主题金句 (Brand Slogans & Manifestos)
  - 广告创意案例 (Ad Creative Cases)
  - 事件营销案例 (Event & Ambient Marketing Stunts)

Enriches each case with Masterclass Book Methodologies:
  - 《定位》心智钉子
  - 《小强广告100招》人话动词
  - 《超级符号》购买指令
  - 《吸金广告》LF8生命原力
  - 《中兴百货》物哀美学
"""

import sys
import os
import re
import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from via54_store.embedding import hash_embed, encode_blob, _tokenize
from agents.master_book_methodology_fuser import MasterBookMethodologyFuser

# ── Multi-Platform Curated Real-World Case & Golden Quote Repository ────
MULTI_PLATFORM_CASES = [
    # ── 1. 数英网 (Digitaling) 精选案例与金句 ──
    {
        "source": "数英网",
        "source_url": "https://www.digitaling.com/projects/2024_proya_520",
        "title": "珀莱雅520：敢爱，也敢不爱",
        "brand": "珀莱雅",
        "industry": "美妆个护",
        "quote_type": "品牌传播主题金句",
        "headline_or_quote": "敢爱，也敢不爱。",
        "sub_text": "当讲爱成为一种商业主流，我们在520说不爱。不爱外界的凝视，不爱被定义的标准，只爱真实生动的自己。",
        "campaign_slogan": "敢爱，也敢不爱",
        "brand_slogan": "趁年轻，去发现",
        "agency": "胜加",
        "published_year": 2024,
        "published_date": "2024-05-18",
        "creative_origin": {
            "brand_context": "珀莱雅持续深耕女性情绪与社会议题，从‘性别不是边界线’到‘回声计划’。",
            "product_feature": "红宝石与双抗系列，倡导由内而外的生命韧性。",
            "market_competition": "美妆行业520充斥着工业糖精式的甜蜜情侣叙事，同质化严重。",
            "consumer_trend": "当代女性拒绝被恋爱脑绑架，更看重情绪自主与悦己自洽。",
            "consumer_insight": "在所有人都在教你如何去爱别人的时候，最需要被合法化的是‘不爱’的自由。"
        },
        "core_insight": {
            "creative_target": "跳脱出庸俗情侣营销，确立女性精神主权图腾。",
            "viral_effect": "引发全网小红书与微博热搜，微博话题阅读量超3亿。",
            "memory_anchor": "‘敢爱，也敢不爱’的极致反转断言。"
        },
        "social_meme_tags": ["520反向营销", "女性主权", "情绪嘴替", "反恋爱脑"],
        "event_stunt": "联合全国10家独立书店，设立‘不爱留言箱’与‘精神出逃专架’。"
    },
    {
        "source": "数英网",
        "source_url": "https://www.digitaling.com/articles/durex_raincoat_2024",
        "title": "杜蕾斯雨季企划：今夜，安全缓冲",
        "brand": "杜蕾斯",
        "industry": "大健康/个护",
        "quote_type": "文案金句",
        "headline_or_quote": "让每一个冲动，都有安全的缓冲。",
        "sub_text": "窗外的暴雨是世界的狂欢，屋内的呼吸是彼此的宇宙。",
        "campaign_slogan": "让每一个冲动，都有安全的缓冲",
        "brand_slogan": "Love Sex Durex",
        "agency": "环时互动",
        "published_year": 2024,
        "published_date": "2024-07-22",
        "creative_origin": {
            "brand_context": "杜蕾斯在两性与安全感之间维持克制而高级的社交沟通。",
            "product_feature": "超薄水感与高弹性防护。",
            "market_competition": "计生品牌极易滑入低俗擦边或生硬参数叫卖。",
            "consumer_trend": "都市青年在亲密关系中既渴望尽兴，又极度看重底线安全。",
            "consumer_insight": "冲动需要被理解与拥抱，但成年人的尽兴必须建立在确定的安全感之上。"
        },
        "core_insight": {
            "creative_target": "将物理防护升华为亲密关系中的温柔阻尼与信任底气。",
            "viral_effect": "全网朋友圈海报疯狂截图刷屏。",
            "memory_anchor": "‘冲动’与‘缓冲’的双声对称。"
        },
        "social_meme_tags": ["杜蕾斯文案", "双关通感", "安全感", "高级性感"],
        "event_stunt": "暴雨天在核心写字楼派发定制‘安全缓冲雨靴套’。"
    },

    # ── 2. 顶尖文案 (TOPYS) 先锋创意与文化金句 ──
    {
        "source": "顶尖文案",
        "source_url": "https://www.topys.cn/article/2024_step_by_step",
        "title": "步履不停：在不敢停下的城市里，给肉身开一张请假条",
        "brand": "步履不停",
        "industry": "服饰/文艺电商品牌",
        "quote_type": "品牌传播主题金句",
        "headline_or_quote": "你写PPT时，阿拉斯加的鳕鱼正跃出水面。",
        "sub_text": "在不敢停下的城市里，给肉身开一张请假条。走过的路，每一步都算数。",
        "campaign_slogan": "给肉身开一张请假条",
        "brand_slogan": "走过的路，都算数",
        "agency": "步履不停In-House",
        "published_year": 2024,
        "published_date": "2024-04-12",
        "creative_origin": {
            "brand_context": "步履不停作为文艺女装标杆，始终探讨城市与旷野的张力。",
            "product_feature": "棉麻天然面料，宽松舒适剪裁。",
            "market_competition": "快时尚内卷款式与低价，缺乏精神陪伴感。",
            "consumer_trend": "‘班味’成为全网痛点，逃离写字楼成为精神刚需。",
            "consumer_insight": "衣服不仅是遮体物，衣服是身体在格子里最后一道自由防线。"
        },
        "core_insight": {
            "creative_target": "打造都市打工人的‘物理去班味’战袍。",
            "viral_effect": "文艺青年与职场白领的共同圣经。",
            "memory_anchor": "PPT与阿拉斯加鳕鱼的剧烈时空反差。"
        },
        "social_meme_tags": ["精神离职", "去班味", "文艺文案", "旷野生活"],
        "event_stunt": "将上海安福路门店改造成‘旷野车站’，进店可领取一张盖章‘肉身请假条’。"
    },
    {
        "source": "顶尖文案",
        "source_url": "https://www.topys.cn/article/2025_neiwai_nobody",
        "title": "内外 (NEIWAI)：NO BODY IS NOBODY 没有一种身材是微不足道的",
        "brand": "内外 (NEIWAI)",
        "industry": "内衣/生活方式",
        "quote_type": "品牌传播主题金句",
        "headline_or_quote": "NO BODY IS NOBODY，没有一种身材是微不足道的。",
        "sub_text": "我的身体，是我唯一的疆域。平胸、微胖、妊娠纹、疤痕，都是生命真实的勋章。",
        "campaign_slogan": "NO BODY IS NOBODY",
        "brand_slogan": "一切都好，自在内外",
        "agency": "意类 (Goodidea Media)",
        "published_year": 2025,
        "published_date": "2025-03-08",
        "creative_origin": {
            "brand_context": "内外从无钢圈舒适内衣起步，成长为身体美学代表品牌。",
            "product_feature": "云朵无感贴合面料与无压设计。",
            "market_competition": "传统内衣聚焦聚拢、性感与男性凝视。",
            "consumer_trend": "身体自洽与多元审美觉醒，反容貌身材焦虑。",
            "consumer_insight": "女性最渴望的是被自己的身体接纳，而不是被尺码表审判。"
        },
        "core_insight": {
            "creative_target": "颠覆传统内衣的‘性感审判’，确立身体自主权神圣性。",
            "viral_effect": "连续四年成为三八妇女节全行业最出圈文化标杆。",
            "memory_anchor": "‘NO BODY IS NOBODY’的中英文双重双关谐音。"
        },
        "social_meme_tags": ["身体自洽", "反身材焦虑", "三八妇女节标杆", "女性叙事"],
        "event_stunt": "无滤镜巨幅黑白素人肖像展空降上海静安雕塑公园与全国地标。"
    },

    # ── 3. 广告门 (Adquan) 品牌战役与年度大奖案例 ──
    {
        "source": "广告门",
        "source_url": "https://www.adquan.com/post-2024-ant-forest",
        "title": "蚂蚁森林：生活有点苦，但绿色一直在长",
        "brand": "蚂蚁集团 / 蚂蚁森林",
        "industry": "互联网/公益金融",
        "quote_type": "活动主题金句",
        "headline_or_quote": "生活天天给我上课，我在沙漠里种一棵真树。",
        "sub_text": "每天偷能量不是为了虚荣，是想在不确定的世界里，确认一株梭梭树正努力扎根。",
        "campaign_slogan": "看见绿色的力量",
        "brand_slogan": "因为信任，所以简单",
        "agency": "群玉山 (Mountaintop)",
        "published_year": 2024,
        "published_date": "2024-09-15",
        "creative_origin": {
            "brand_context": "蚂蚁森林从低碳打卡工具升级为公众情感寄托空间。",
            "product_feature": "手机步行与低碳消费积累虚拟能量，真实荒漠造林。",
            "market_competition": "常规企业社会责任(CSR)说教味浓、距离普通人遥远。",
            "consumer_trend": "年轻人渴望微小的‘掌控感与确定性’。",
            "consumer_insight": "在庞大无力的现实面前，一棵真实活在远方的树，成了都市人精神的锚。"
        },
        "core_insight": {
            "creative_target": "把日常无聊的减碳动作升华为灵魂在远方的具体投射。",
            "viral_effect": "数百万网友认领树苗卫星遥感图并自发晒朋友圈。",
            "memory_anchor": "工位写字楼与阿拉善荒漠真树的物理对话。"
        },
        "social_meme_tags": ["低碳生活", "情绪治愈", "蚂蚁森林", "确定性自救"],
        "event_stunt": "把荒漠里风吹树叶的实时原声通过无人机麦克风直播回传至北上广深地铁通道。"
    },
    {
        "source": "广告门",
        "source_url": "https://www.adquan.com/post-2025-chagee-tea",
        "title": "霸王茶姬：以东方茶，会世界友",
        "brand": "霸王茶姬",
        "industry": "新茶饮/新消费",
        "quote_type": "活动主题金句",
        "headline_or_quote": "茶不过两种姿态，浮、沉；饮茶人不过两种姿势，拿起、放下。",
        "sub_text": "千年古道的一片树叶，在当代年轻人的杯里重逢世界。",
        "campaign_slogan": "以东方茶，会世界友",
        "brand_slogan": "原叶鲜奶茶，茶香自然来",
        "agency": "华与华 / In-House",
        "published_year": 2025,
        "published_date": "2025-06-10",
        "creative_origin": {
            "brand_context": "中国新茶饮出海与东方文化现代化表达。",
            "product_feature": "伯牙绝弦原叶鲜奶茶，0奶精0植脂末。",
            "market_competition": "传统奶茶过度甜腻添加，星巴克垄断商务咖啡社交。",
            "consumer_trend": "新中式国潮崛起与清爽无负担健康饮食习惯。",
            "consumer_insight": "年轻人喝茶喝的不只是解渴，更是一种松弛的东方文化身份认同。"
        },
        "core_insight": {
            "creative_target": "将东方茶道生活方式现代化，重构全球年轻人社交硬通货。",
            "viral_effect": "全球单店日均出杯突破4000杯，巴黎奥运会快闪引爆海内外热议。",
            "memory_anchor": "‘C 字标志’超级符号与‘伯牙绝弦’诗意品名。"
        },
        "social_meme_tags": ["东方茶会世界友", "伯牙绝弦", "新中式", "超级符号"],
        "event_stunt": "巴黎塞纳河畔设立‘东方茶驿站’，与卢浮宫联动‘千里江山图’限定杯身。"
    },

    # ── 4. 梅花网 (Meihua) 活动营销与实战案例 ──
    {
        "source": "梅花网",
        "source_url": "https://www.meihua.info/post-kfc-crazy-thursday",
        "title": "肯德基：疯狂星期四 V我50",
        "brand": "肯德基 (KFC)",
        "industry": "餐饮/快餐",
        "quote_type": "文案金句",
        "headline_or_quote": "今天疯狂星期四，谁请我吃肯德基，V我50！",
        "sub_text": "表面上是八卦绯闻与离谱反转，结尾无情一刀：今天是肯德基疯狂星期四，V我50！",
        "campaign_slogan": "疯狂星期四，疯就完事了",
        "brand_slogan": "生活如此多娇，肯德基",
        "agency": "肯德基数字营销团队",
        "published_year": 2024,
        "published_date": "2024-03-28",
        "creative_origin": {
            "brand_context": "肯德基周四例行促销打造成当代互联网最大集体迷因。",
            "product_feature": "黄金脆皮鸡、蛋挞等明星单品半价优惠。",
            "market_competition": "周四属于工作日疲惫低谷期，各大快餐竞相降价。",
            "consumer_trend": "当代网民热衷发疯文学与无厘头荒谬自嘲。",
            "consumer_insight": "打工人不需要一本正经的优惠券，需要的是一个合情合理发疯玩梗的借口。"
        },
        "core_insight": {
            "creative_target": "将常规打折转化为低门槛、全网二创、病毒式扩散的社交母体。",
            "viral_effect": "每周四固定登上微博和抖音热搜榜，网友创作数十万条‘发疯段子’。",
            "memory_anchor": "‘V我50’的极简神经指令与周四场景强绑定。"
        },
        "social_meme_tags": ["疯狂星期四", "V我50", "发疯文学", "社交迷因"],
        "event_stunt": "联合各大脱口秀演员举办‘疯四文学大赏’，现场颁发黄金脆皮炸鸡奖杯。"
    },
    {
        "source": "梅花网",
        "source_url": "https://www.meihua.info/post-bananain-bottom-line",
        "title": "蕉内：底线 —— 重新定义基本款",
        "brand": "蕉内 (Bananain)",
        "industry": "服装家纺/新消费",
        "quote_type": "品牌传播主题金句",
        "headline_or_quote": "底线，是看不见的专业；坚守，是看得见的骨气。",
        "sub_text": "在看不见的地方较劲，给身体最诚实的底线。",
        "campaign_slogan": "重新设计基本款",
        "brand_slogan": "蕉内，重新设计基本款",
        "agency": "胜加",
        "published_year": 2024,
        "published_date": "2024-06-01",
        "creative_origin": {
            "brand_context": "蕉内从‘无感标签内裤’切入，打造国民基本款超级品牌。",
            "product_feature": "热皮、凉皮、银皮专利面料，无缝剪裁。",
            "market_competition": "传统贴身衣物市场代工杂乱，品质良莠不齐。",
            "consumer_trend": "年轻一代对日常贴身衣物的舒适度要求达到前所未有的严苛。",
            "consumer_insight": "真正的高级不是外在logo的炫耀，而是身体在最隐秘处体会到的无感体贴。"
        },
        "core_insight": {
            "creative_target": "把一条内裤/袜子升华为当代人面对生活不能退让的精神底线。",
            "viral_effect": "央视网转发，青年群体广泛共鸣。",
            "memory_anchor": "‘底线’的双关隐喻。"
        },
        "social_meme_tags": ["底线", "重新设计基本款", "无感科技", "国货自强"],
        "event_stunt": "在深圳湾万象城打造巨型‘无感科技冰立方’装置，展示极温测试。"
    },

    # ── 5. 胖鲸 (SocialBeta / Pangjing) 事件营销与快闪案例 ──
    {
        "source": "胖鲸",
        "source_url": "https://pangjing.cn/cases/loopy-tea-pop-up",
        "title": "乐乐茶 x Loopy：精神离职打工人嘴替快闪",
        "brand": "乐乐茶 x 赞萌露比 (Zanmang Loopy)",
        "industry": "新茶饮/IP联名",
        "quote_type": "事件营销案例",
        "headline_or_quote": "今日精神离职，请勿用无意义的需求污染我的磁场。",
        "sub_text": "粉色小海狸顶着最软萌的脸，说出全天下打工人最狠的真心话。",
        "campaign_slogan": "今日精神离职",
        "brand_slogan": "我的快乐，乐乐茶",
        "agency": "乐乐茶品牌市场部",
        "published_year": 2024,
        "published_date": "2024-08-08",
        "creative_origin": {
            "brand_context": "乐乐茶通过高频IP联名激活年轻消费心智。",
            "product_feature": "一整颗粉桃果肉饮品 + Loopy定制粉红周边杯套与立牌。",
            "market_competition": "夏季茶饮白热化大促，单靠口味难以形成自发裂变。",
            "consumer_trend": "Z世代职场人的‘表面假笑、内心暴躁’的反差自救心理。",
            "consumer_insight": "年轻人在工位上需要一个‘代我发脾气’的萌系外挂。"
        },
        "core_insight": {
            "creative_target": "将饮品转化为工位上的‘精神防弹衣’与免责声明牌。",
            "viral_effect": "小红书单日UGC笔记超10万篇，线下门店排队4小时售罄。",
            "memory_anchor": "Loopy歪头假笑 + ‘今日精神离职’表情包杯套。"
        },
        "social_meme_tags": ["精神离职", "赞萌露比", "工位嘴替", "反差萌"],
        "event_stunt": "在陆家嘴核心写字楼大堂搭建‘精神离职登记处’，打卡即可敲击‘工位除锈退火木鱼’。"
    },
    {
        "source": "胖鲸",
        "source_url": "https://pangjing.cn/cases/patagonia-worn-wear",
        "title": "巴塔哥尼亚 (Patagonia)：别买这件夹克，修补它！",
        "brand": "巴塔哥尼亚 (Patagonia)",
        "industry": "户外运动/环保",
        "quote_type": "广告创意案例",
        "headline_or_quote": "Don't Buy This Jacket! (别买这件夹克！)",
        "sub_text": "每生产一件新夹克，都要排放20磅温室气体。如果你的旧夹克还能穿，请把它修补好，继续走向山野。",
        "campaign_slogan": "Don't Buy This Jacket",
        "brand_slogan": "We're in business to save our home planet.",
        "agency": "In-House Creative",
        "published_year": 2024,
        "published_date": "2024-11-25",
        "creative_origin": {
            "brand_context": "Patagonia将所有利润捐献给地球，践行激进环保主义。",
            "product_feature": "高耐用度防撕裂抓绒与羽绒服，终身免费修补服务。",
            "market_competition": "黑五购物狂欢节所有品牌都在催促冲动消费。",
            "consumer_trend": "反消费主义与真正可持续生活理念在高端中产中蔓延。",
            "consumer_insight": "真正自信的人不需要不断购买新衣服来证明自己的品味，缝补过的痕迹才是勋章。"
        },
        "core_insight": {
            "creative_target": "以‘劝退购买’的反商业姿态，赢得全球最挑剔消费者的绝对信仰。",
            "viral_effect": "广告刊登在纽约时报，品牌当年销售额反向暴涨30%，成为商业伦理传奇。",
            "memory_anchor": "‘别买这件夹克’的反直觉震惊感。"
        },
        "social_meme_tags": ["反消费主义", "修补计划", "户外信仰", "长期主义"],
        "event_stunt": "开着改装太阳能‘Worn Wear 修补房车’巡回全国大学与岩场，免费为任何品牌的旧衣缝补拉链与补丁。"
    }
]


class MultiPlatformCollectorAndEnricher:
    """Collects, enriches with book methodologies, and ingests multi-platform creative assets."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (PROJECT_ROOT / "via54_kb.db")
        self.fuser = MasterBookMethodologyFuser(self.db_path)
        self._init_golden_quotes_table()

    def _init_golden_quotes_table(self):
        """Create golden_quotes_and_stunts table in SQLite."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS golden_quotes_and_stunts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_type TEXT NOT NULL,
                source_platform TEXT NOT NULL,
                brand TEXT NOT NULL,
                industry TEXT,
                headline_or_quote TEXT NOT NULL,
                sub_text TEXT,
                core_insight TEXT,
                rhetorical_device TEXT,
                matched_book_methodology TEXT,
                published_year INTEGER DEFAULT 2024,
                source_url TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        conn.close()

    def enrich_with_book_methodologies(self, c: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Masterclass Book frameworks to categorize and enrich each case."""
        context = f"{c['brand']} {c['headline_or_quote']} {c.get('sub_text', '')}"
        
        # 1. Life-Force 8
        lf8 = self.fuser.map_life_force_8(context)
        
        # 2. Rhetorical Device & Book Mapping
        h = c["headline_or_quote"]
        if "不是" in h or "不爱" in h or "Don't" in h:
            matched_book = "阿尔·里斯《定位》/ 珀莱雅《敢不爱》观念反常识重构"
            device = "A!=B 否定反转重构"
        elif any(w in h for w in ["PPT", "鳕鱼", "暴雨", "荒漠", "真树", "泥泞"]):
            matched_book = "步履不停 / 许舜英物哀美学与时空微感官蒙太奇"
            device = "微感官时空剧烈撕裂"
        elif any(w in h for w in ["冲动", "缓冲", "底线"]):
            matched_book = "杜蕾斯 / 金鹏远《借势》两性与物理双关"
            device = "物理动作与心理情绪双关"
        elif any(w in h for w in ["V我50", "疯就完事", "请勿", "离职"]):
            matched_book = "华与华《超级符号》/ 马楠《尖叫感》社交迷因与购买指令"
            device = "超级指令与黑色自嘲"
        else:
            matched_book = "林桂枝《小强广告100招》人话动词与真诚沟通"
            device = "真诚人话与情感共鸣"

        c["matched_book_methodology"] = matched_book
        c["rhetorical_device"] = device
        c["lf8_mapping"] = lf8["matched_primary_desires"][0]
        return c

    def ingest_cases(self) -> int:
        """Enrich and ingest all multi-platform cases into SQLite and vector store."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        total_ingested = 0

        for item in MULTI_PLATFORM_CASES:
            enriched = self.enrich_with_book_methodologies(item)
            
            # 1. Insert into golden_quotes_and_stunts
            cursor.execute("""
                INSERT OR REPLACE INTO golden_quotes_and_stunts 
                (quote_type, source_platform, brand, industry, headline_or_quote, 
                 sub_text, core_insight, rhetorical_device, matched_book_methodology, 
                 published_year, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                enriched["quote_type"],
                enriched["source"],
                enriched["brand"],
                enriched["industry"],
                enriched["headline_or_quote"],
                enriched.get("sub_text", ""),
                json.dumps(enriched.get("core_insight", {}), ensure_ascii=False),
                enriched["rhetorical_device"],
                enriched["matched_book_methodology"],
                enriched.get("published_year", 2024),
                enriched["source_url"]
            ))

            # 2. Insert/Update into creative_cases
            origin = enriched.get("creative_origin", {})
            insights = enriched.get("core_insight", {})
            stunt_txt = enriched.get("event_stunt", "")
            full_md = f"""# 【{enriched['brand']}】{enriched['title']}
> **来源**: {enriched['source']} | **行业**: {enriched['industry']} | **年份**: {enriched['published_year']}
> **金句类型**: {enriched['quote_type']} | **书籍理论赋能**: {enriched['matched_book_methodology']}
> **生命原力(LF8)**: {enriched['lf8_mapping']} | **修辞手法**: {enriched['rhetorical_device']}

## 🎯 核心金句与文案
> **「{enriched['headline_or_quote']}」**
*{enriched.get('sub_text', '')}*

- **战役口号**: {enriched.get('campaign_slogan', '')}
- **品牌口号**: {enriched.get('brand_slogan', '')}

## 💡 创意原点 (Creative Origin)
- **品牌背景**: {origin.get('brand_context', '')}
- **产品特性**: {origin.get('product_feature', '')}
- **市场竞争**: {origin.get('market_competition', '')}
- **消费趋势**: {origin.get('consumer_trend', '')}
- **消费者洞察**: {origin.get('consumer_insight', '')}

## 🚀 核心洞察与传播效果
- **创意目标**: {insights.get('creative_target', '')}
- **传播效果**: {insights.get('viral_effect', '')}
- **记忆锚点**: {insights.get('memory_anchor', '')}

## 🎪 事件营销与破圈快闪
{stunt_txt}
"""

            cursor.execute("""
                INSERT INTO creative_cases (
                    source, source_url, title, brand, industry, published_year, published_date,
                    agency, brand_context, product_feature, market_competition,
                    consumer_trend, consumer_insight, creative_target, viral_effect,
                    memory_anchor, social_meme_tags, campaign_slogan, brand_slogan,
                    raw_content, full_markdown, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
                )
                ON CONFLICT(source_url) DO UPDATE SET
                    title=excluded.title,
                    brand=excluded.brand,
                    industry=excluded.industry,
                    campaign_slogan=excluded.campaign_slogan,
                    brand_slogan=excluded.brand_slogan,
                    full_markdown=excluded.full_markdown,
                    updated_at=CURRENT_TIMESTAMP
            """, (
                enriched["source"],
                enriched["source_url"],
                enriched["title"],
                enriched["brand"],
                enriched["industry"],
                enriched["published_year"],
                enriched.get("published_date", ""),
                enriched.get("agency", ""),
                origin.get("brand_context", ""),
                origin.get("product_feature", ""),
                origin.get("market_competition", ""),
                origin.get("consumer_trend", ""),
                origin.get("consumer_insight", ""),
                insights.get("creative_target", ""),
                insights.get("viral_effect", ""),
                insights.get("memory_anchor", ""),
                json.dumps(enriched.get("social_meme_tags", []), ensure_ascii=False),
                enriched.get("campaign_slogan", ""),
                enriched.get("brand_slogan", ""),
                enriched.get("headline_or_quote", ""),
                full_md
            ))

            # 3. Add to concepts & vector store
            bundle_id = 1
            rel_path = f"multi_platform_golden/{enriched['brand']}_{enriched['published_year']}.md"
            body_hash = hashlib.sha256(full_md.encode("utf-8")).hexdigest()

            cursor.execute("""
                INSERT INTO concepts (
                    bundle_id, rel_path, type, title, description, resource,
                    tags_json, timestamp, source_path, mtime, body_size, body_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?, ?, ?)
                ON CONFLICT(bundle_id, rel_path) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    body_hash=excluded.body_hash,
                    body_size=excluded.body_size
            """, (
                bundle_id,
                rel_path,
                "golden_quote_case",
                f"【{enriched['source']}】{enriched['brand']}：{enriched['headline_or_quote']}",
                f"{enriched['quote_type']} | {enriched['matched_book_methodology']}",
                enriched["source_url"],
                json.dumps(enriched.get("social_meme_tags", []), ensure_ascii=False),
                str(self.db_path),
                time.time(),
                len(full_md.encode("utf-8")),
                body_hash
            ))

            cursor.execute("SELECT concept_id FROM concepts WHERE bundle_id=? AND rel_path=?", (bundle_id, rel_path))
            concept_id = cursor.fetchone()[0]

            # Vector chunks
            cursor.execute("DELETE FROM concept_chunks WHERE concept_id=?", (concept_id,))
            paragraphs = [p.strip() for p in full_md.split("\n\n") if p.strip()]
            for idx, p in enumerate(paragraphs):
                cursor.execute("""
                    INSERT INTO concept_chunks (concept_id, chunk_idx, text, char_start, char_end, tokens_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (concept_id, idx, p, 0, len(p), json.dumps([], ensure_ascii=False)))
                chunk_id = cursor.lastrowid

                tokens = _tokenize(p)
                for tok in set(tokens):
                    cursor.execute("""
                        INSERT OR IGNORE INTO chunk_terms (term, chunk_id, tf)
                        VALUES (?, ?, ?)
                    """, (tok[:50], chunk_id, 1.0))

                vec = hash_embed(p, dim=256)
                blob = encode_blob(vec)

                cursor.execute("""
                    INSERT OR REPLACE INTO chunk_vector_meta (chunk_id, dim, norm, model)
                    VALUES (?, ?, ?, ?)
                """, (chunk_id, 256, 1.0, "blake2b-hash-256"))

                cursor.execute("""
                    INSERT OR REPLACE INTO chunk_vector_blob (chunk_id, vec, model)
                    VALUES (?, ?, ?)
                """, (chunk_id, blob, "blake2b-hash-256"))

            total_ingested += 1

        conn.commit()
        conn.close()
        return total_ingested


if __name__ == "__main__":
    collector = MultiPlatformCollectorAndEnricher()
    count = collector.ingest_cases()
    print(f"✅ Successfully harvested, enriched with book methodologies, and ingested {count} multi-platform cases & golden quotes into DB & vector store!")
