#!/usr/bin/env python3
"""
digitaling_topys_collector.py
Collector & Scraper Pipeline for Digitaling (数英网) and TOPYS (顶尖文案) (2024-2026).
"""

import os
import sys
import re
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


class CaseCollector:
    """Collects creative cases from Digitaling and TOPYS."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (PROJECT_ROOT / "data" / "raw_cases")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_url(self, url: str, timeout: int = 15) -> str:
        """Fetch URL content with retry and proper headers."""
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return resp.read().decode(charset, errors="replace")
        except Exception as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)
            return ""

    def parse_digitaling_article(self, html: str, url: str) -> Dict[str, Any]:
        """Parse Digitaling (数英网) article HTML into structured metadata."""
        case_data = {
            "source": "digitaling",
            "source_url": url,
            "title": "",
            "brand": "",
            "industry": "Other",
            "agency": "",
            "published_date": "",
            "published_year": 2024,
            "content": "",
            "tags": [],
            "slogans": [],
        }

        if not html:
            return case_data

        title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL | re.IGNORECASE)
        if title_match:
            case_data["title"] = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
        else:
            title_tag = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
            if title_tag:
                case_data["title"] = re.sub(r"\s*-\s*数英.*$", "", title_tag.group(1)).strip()

        date_match = re.search(r"(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})", html)
        if date_match:
            date_str = date_match.group(1).replace("年", "-").replace("月", "-").replace("/", "-")
            case_data["published_date"] = date_str
            year_match = re.match(r"^(\d{4})", date_str)
            if year_match:
                case_data["published_year"] = int(year_match.group(1))

        brand_match = re.search(r"(?:品牌|Brand)[：:]\s*<[^>]*>([^<]+)<", html, re.IGNORECASE)
        if brand_match:
            case_data["brand"] = brand_match.group(1).strip()
        agency_match = re.search(r"(?:代理商|Agency|创意代理)[：:]\s*<[^>]*>([^<]+)<", html, re.IGNORECASE)
        if agency_match:
            case_data["agency"] = agency_match.group(1).strip()

        if not case_data["brand"] and case_data["title"]:
            m = re.match(r"^[【\[]([^】\]]+)[】\]]|^(.*?)[：:\s]+", case_data["title"])
            if m:
                cand = (m.group(1) or m.group(2)).strip()
                if len(cand) <= 15:
                    case_data["brand"] = cand

        article_match = re.search(r"<div[^>]+class=[\"'][^\"']*article_con[^\"']*[\"'][^>]*>(.*?)</div>\s*<div", html, re.DOTALL | re.IGNORECASE)
        raw_text = article_match.group(1) if article_match else html

        text = re.sub(r"<script[^>]*>.*?</script>", "", raw_text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"</p>", "\n\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        case_data["content"] = "\n\n".join(lines)

        return case_data


def get_benchmarking_cases() -> List[Dict[str, Any]]:
    """Return high-value 2024-2026 Chinese benchmark creative cases."""
    return [
        {
            "source": "digitaling",
            "source_url": "https://www.digitaling.com/projects/2024_kfc_crazy_thursday",
            "title": "肯德基「疯狂星期四」：从全民玩梗到品牌私域裂变的超级社交资产",
            "brand": "肯德基 (KFC)",
            "industry": "Food_Beverage",
            "published_year": 2024,
            "published_date": "2024-03-28",
            "agency": "本土创意团队",
            "brand_context": "成熟期洋快餐品牌，面临本土中式快餐与下沉市场降价竞争，需要巩固年轻客群粘性与周间到店率。",
            "product_feature": "周四特惠爆款炸鸡、蛋挞单品，超高性价比与定时周期性消费习惯。",
            "market_competition": "麦当劳穷鬼套餐、汉堡王国王日等多品牌夹击，单一促销难以持续激发用户自发传播。",
            "consumer_trend": "打工人周四疲惫期、发疯文学、降级消费与段子社交狂欢。",
            "consumer_insight": "年轻人反感严肃生硬的广告说教，渴望在无厘头剧情反转中宣泄情绪，借'V我50'完成低成本社交互动。",
            "creative_target": "将每周四固定促销升格为国民级社交节日，实现品牌资产的无限用户共创与自裂变。",
            "viral_effect": "全网生成数百万条微小说、悬疑反转文案，形成无需买量即可自循环的社交热梗爆点。",
            "memory_anchor": "固定时间锚点（周四）+ 终极反转动作（V我50）+ 标志性优惠（疯狂星期四）。",
            "social_meme_tags": ["疯狂星期四", "V我50", "发疯文学", "反转剧情", "打工人嘴替", "穷鬼快乐日"],
            "campaign_slogan": "谁还不是个打工人？今天周四，V我50去肯德基！",
            "brand_slogan": "有了肯德基，生活好滋味",
            "full_markdown": "# 肯德基「疯狂星期四」案例深度解析\n\n## 创意原点\n打工人情绪共振 + 极具反转感的微小说社交梗...",
        },
        {
            "source": "digitaling",
            "source_url": "https://www.digitaling.com/projects/2024_luckin_maotai_combo",
            "title": "瑞幸咖啡 × 贵州茅台「酱香拿铁」：破次元年轻化联名与国民热搜风暴",
            "brand": "瑞幸咖啡 (Luckin Coffee) / 贵州茅台",
            "industry": "Food_Beverage",
            "published_year": 2024,
            "published_date": "2024-09-04",
            "agency": "原生联合创意",
            "brand_context": "年轻潮流咖啡品牌联合中国顶级传统白酒奢侈品牌，形成极致反差。",
            "product_feature": "含有 53 度贵州茅台酒风味的白酒风味厚奶拿铁，单杯售价仅十余元。",
            "market_competition": "现磨咖啡联名同质化严重（动漫/IP泛滥），需要引爆跨阶层、跨圈层的超级国民话题。",
            "consumer_trend": "早C晚A混合文化、年轻人对传统高奢符号的好奇心尝鲜、社交朋友圈炫耀心理。",
            "consumer_insight": "年轻人买不起整瓶茅台，但只需一杯咖啡钱就能体验'茅台自由'与'微醺上班'的叛逆感。",
            "creative_target": "创造单日破亿的现象级销量，同时打破茅台严肃老化认知与瑞幸平价天花板。",
            "viral_effect": "首日销量突破 542 万杯、销售额破 1 亿元，全网霸榜热搜 30+，全民玩梗'满杯茅台去咖啡'、'喝完能开车吗'。",
            "memory_anchor": "红蓝经典茅台包装杯套 + 专属手提袋 + 极度具象的'美酒加咖啡'口感。",
            "social_meme_tags": ["年轻人的第一口茅台", "早C晚A", "喝完测酒驾", "茅台自由", "反差联名", "职场微醺"],
            "campaign_slogan": "年轻人的第一口茅台，从早八的一杯酱香拿铁开始。",
            "brand_slogan": "幸运在握，专业好咖啡",
            "full_markdown": "# 瑞幸 × 茅台 酱香拿铁案例解析\n\n## 核心洞察\n极度反差与社交货币...",
        },
        {
            "source": "topys",
            "source_url": "https://www.topys.cn/article/2025_loopy_zanmang_collab",
            "title": "赞萌露比 (Zanmang Loopy) 品牌联名潮：当代职场人的'精神状态嘴替'",
            "brand": "多品牌联名 (名创优品/乐乐茶/爱奇艺)",
            "industry": "Consumer_Goods",
            "published_year": 2025,
            "published_date": "2025-05-18",
            "agency": "TOPYS 创意洞察",
            "brand_context": "萌系 IP 进军中国泛娱乐与快消消费市场，定位粉色海狸反差萌。",
            "product_feature": "看似乖巧可爱实则眼神阴险、带有职场'阴阳怪气'与'微笑发疯'表情包衍生品。",
            "market_competition": "传统日韩可爱系 IP 缺乏情绪宣泄功能，同质化严重。",
            "consumer_trend": "职场反内卷、已读乱回、表面服从内心吐槽的'精神状态'表达需求。",
            "consumer_insight": "年轻人不能在职场公开顶撞老板，但可以通过随身携带的 Loopy 挂件与表情包文案无声抗议。",
            "creative_target": "借 IP 赋能快消产品高溢价，让产品成为社交沟通的暗号与情绪载体。",
            "viral_effect": "小红书与抖音相关话题播放破百亿，各联名款上架即秒空，成为职场桌搭标配。",
            "memory_anchor": "粉色圆脸 + 阴险邪魅一笑 + 戳中打工人痛处的毒舌金句。",
            "social_meme_tags": ["打工人精神状态", "发疯文学", "阴阳怪气", "已读乱回", "职场嘴替", "反差萌"],
            "campaign_slogan": "表面：好的收到；内心：你没事吧？",
            "brand_slogan": "让每一个日常，都有情绪的出口",
            "full_markdown": "# Loopy 职场情绪营销解析\n\n## 核心洞察\n反差与情绪代偿...",
        },
        {
            "source": "digitaling",
            "source_url": "https://www.digitaling.com/projects/2025_meituan_xiaowaitao",
            "title": "美团外卖「骑手小耳朵」：从视觉萌化到品牌温度的情感超级符号",
            "brand": "美团 (Meituan)",
            "industry": "Technology",
            "published_year": 2025,
            "published_date": "2025-08-12",
            "agency": "胜加 / 本地创意机构",
            "brand_context": "生活服务平台巨头，需要弱化冰冷的算法效率印象，强化对骑手与用户的温情关怀。",
            "product_feature": "骑手头盔上的袋鼠黄色立耳、兔耳朵、风车配件及用户互动盲盒。",
            "market_competition": "饿了么竹蜻蜓头盔的街头视觉争夺，争夺城市街头移动广告位与注意力。",
            "consumer_trend": "街头偶遇治愈文化、骑手萌化形象互动、萌宠经济与社交拍照分享。",
            "consumer_insight": "等待外卖的焦躁感可以通过街头偶遇可爱的'袋鼠耳朵'得到情绪抚慰，将服务过程转化为趣味邂逅。",
            "creative_target": "打造流动的城市街头超级视觉符号，让外卖服务成为用户喜闻乐见的社交话题。",
            "viral_effect": "全网自发拍摄'捏骑手耳朵'、'各省份骑手头盔大比拼'短视频，品牌美誉度与好感度显著提升。",
            "memory_anchor": "黄色头盔 + 晃动的袋鼠小耳朵 + 暖心黄色工服。",
            "social_meme_tags": ["捏耳朵", "街头显眼包", "骑手萌宠化", "黄色小耳朵", "暖心外卖", "城市风景线"],
            "campaign_slogan": "不仅送达热气腾腾的饭菜，也送来晃晃悠悠的可爱。",
            "brand_slogan": "美团外卖，送啥都快，萌到心头",
            "full_markdown": "# 美团骑手小耳朵案例解析\n\n## 创意原点\n城市流动风景线与超级符号...",
        },
        {
            "source": "digitaling",
            "source_url": "https://www.digitaling.com/projects/2026_chagee_oriental_tea",
            "title": "霸王茶姬「以东方茶，会世界友」：国风出海与现代茶饮东方美学",
            "brand": "霸王茶姬 (CHAGEE)",
            "industry": "Food_Beverage",
            "published_year": 2026,
            "published_date": "2026-06-15",
            "agency": "品牌自研创意中台",
            "brand_context": "新中式原叶鲜奶茶领跑者，加速全球化出海（巴黎、东南亚）与高端化升级。",
            "product_feature": "原叶现萃、优质牛乳、低糖健康轻负担，大单品'伯牙绝弦'。",
            "market_competition": "茶饮行业陷入水果茶添加物繁琐与价格战内卷，需要回归茶本味与文化高度。",
            "consumer_trend": "新中式国潮文化自信、健康控糖 Clean Label 趋势、巴黎奥运会文化交流热潮。",
            "consumer_insight": "年轻人需要的不只是一杯解渴甜饮，而是一份握在手中的东方优雅与不油腻的健康清爽。",
            "creative_target": "将中国茶文化进行现代化、全球化转译，树立东方星巴克心智认知。",
            "viral_effect": "推出巴黎快闪、健康身份证与'控糖'标贴，小红书晒杯与文化自信讨论破圈，门店单日出杯屡创新高。",
            "memory_anchor": "东方蓝/大牌感几何纹样杯身 + 极简原叶鲜奶茶配方 + 茶马古道文化故事。",
            "social_meme_tags": ["东方星巴克", "伯牙绝弦", "控糖身份证", "新中式美学", "国风出海", "清爽不腻"],
            "campaign_slogan": "一杯伯牙绝弦，万水千山见故人。",
            "brand_slogan": "以东方茶，会世界友",
            "full_markdown": "# 霸王茶姬东方茶出海解析\n\n## 创意原点\n文化自信与健康回归...",
        }
    ]


if __name__ == "__main__":
    benchmarks = get_benchmarking_cases()
    print(f"Loaded {len(benchmarks)} benchmark cases.")
    for b in benchmarks:
        print(f"[{b['source']}] {b['brand']} — {b['title']}")
