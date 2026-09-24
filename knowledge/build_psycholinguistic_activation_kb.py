#!/usr/bin/env python3
"""
build_psycholinguistic_activation_kb.py
Builds the Psycholinguistic & Neuro-Cognitive Activation Knowledge Base:
Deeply maps 10 seminal psychology schools, landmark research papers, neuroscience mechanisms,
and linguistic activation algorithms that trigger human emotion, subconscious memory, and consumer decisions:
  1. 具身认知与运动/感觉皮层神经拟真 (Pulvermüller, González, Bargh, Lakoff & Johnson)
  2. 躯体标记假说与腹内侧前额叶直觉决策 (Antonio Damasio, Baba Shiv)
  3. 乔纳·伯杰 SPEACC 语言影响与转化矩阵 (Jonah Berger, Bryan & Walton)
  4. 语言范畴模型与动词具身层级 (Semin & Fiedler LCM, Schellekens, Packard & Berger)
  5. 元认知加工流畅度与押韵真理效应 (Alter & Oppenheimer, Reber & Schwarz, McGlone)
  6. 调节聚焦理论与动机语境匹配 (E. Tory Higgins, Jennifer Aaker & Angela Lee)
  7. 说话者-倾听者神经耦合与叙事脑共振 (Uri Hasson, Paul Zak)
  8. VAD 情感三维坐标与高唤醒生理驱动 (Warriner, Kuperman & Brysbaert, Russell)
  9. 语音象征学与布巴-奇奇跨模态感官通感 (Ramachandran & Hubbard, Klink, Yorkston & Menon)
  10. 心智无意识“因为”启发式与前景理论损失厌恶 (Ellen Langer, Tversky & Kahneman)
"""

import sys
import os
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PSYCHOLINGUISTIC_CANON: List[Dict[str, Any]] = [
    {
        "id": 1,
        "school_name_cn": "具身认知与感觉/运动皮层神经拟真",
        "school_name_en": "Embodied Cognition & Somatosensory/Motor Cortical Simulation",
        "key_figures": "Friedemann Pulvermüller, Julio González, Lawrence Williams, John Bargh, George Lakoff, Mark Johnson",
        "seminal_papers_and_books": json.dumps([
            "Pulvermüller, F. (2005). Brain mechanisms linking language and action. Nature Reviews Neuroscience, 6(7), 576-582.",
            "González, J., Barros-Loscertales, A., Pulvermüller, F., et al. (2006). Reading cinnamon activates olfactory brain regions. NeuroImage, 32(2), 906-912.",
            "Williams, L. E., & Bargh, J. A. (2008). Experiencing physical warmth promotes interpersonal warmth. Science, 322(5901), 606-607.",
            "Lakoff, G., & Johnson, M. (1980/2003). Metaphors We Live By. University of Chicago Press."
        ], ensure_ascii=False),
        "core_psychological_mechanism": (
            "大脑并非孤立抽象的符号处理机，语言解码深度依赖生理感觉与运动神经系统的即时再激活（Neural Simulation）。"
            "当受众阅读具象动作动词（如‘撕开’、‘嚼碎’、‘奔袭’）时，大脑直接激活躯体运动皮层（Motor Cortex）；"
            "当阅读气味或触觉词汇（如‘肉桂’、‘砂砾’、‘冰镇’）时，嗅觉梨状皮层（Piriform Cortex）与第一感觉皮层直接放电。"
            "概念隐喻将物理体验映射至抽象心理：物理温度启动社交温暖，物理重力启动价值严肃。"
        ),
        "neural_regions_activated": "躯体感觉皮层 (S1), 运动皮层 (M1), 梨状皮层/杏仁核 (Olfactory), 脑岛 (Insular Cortex)",
        "linguistic_markers": json.dumps({
            "motor_verbs": ["撕", "咬", "踩", "奔", "拔", "握", "跃", "劈", "推", "扣"],
            "sensory_textures": ["温热", "冰凉", "粗糙", "细腻", "酥脆", "醇厚", "微苦", "清冽", "刺痛"],
            "spatial_metaphors": ["向上", "沉潜", "拔高", "拓宽", "穿透", "落地"]
        }, ensure_ascii=False),
        "algorithmic_metric_formula": "Embodied_Simulation_Index = (Count(Motor_Verbs) * 1.5 + Count(Sensory_Textures) * 1.2) / Total_Words",
        "copywriting_application_insight": (
            "拒绝抽象副词与空洞修饰。用‘撕开晨雾’替代‘开启美好的清晨’，用‘指尖可触的温润’替代‘高品质陶瓷质感’。"
            "让消费者的感官神经元在看到文字的第 0.1 秒先于理性做出物理生理反应。"
        ),
        "canonical_benchmark_cases": "耐克《跑下去，天自己会亮》、苹果《把 1000 首歌装进口袋》、全联《长得漂亮是本钱，把钱花得漂亮是本事》"
    },
    {
        "id": 2,
        "school_name_cn": "躯体标记假说与腹内侧前额叶直觉决策",
        "school_name_en": "Somatic Marker Hypothesis & Ventromedial Prefrontal Intuitive Decision",
        "key_figures": "Antonio Damasio (安东尼奥·达马西奥), Hanna Damasio, Antoine Bechara, Baba Shiv",
        "seminal_papers_and_books": json.dumps([
            "Damasio, A. R. (1994). Descartes' Error: Emotion, Reason, and the Human Brain. Putnam Publishing.",
            "Damasio, A. R., Tranel, D., & Damasio, H. (1991). Somatic markers and the guidance of behaviour: theory and preliminary testing.",
            "Bechara, A., Damasio, H., Tranel, D., & Damasio, A. R. (1997). Deciding advantageously before knowing the advantageous strategy. Science, 275(5304), 1293-1295.",
            "Shiv, B., & Fedorikhin, A. (1999). Heart and mind in conflict: The interplay of affect and cognition in consumer decision making. JCR, 26(3), 278-292."
        ], ensure_ascii=False),
        "core_psychological_mechanism": (
            "人类在面对复杂或不确定的选择时，纯逻辑推演会导致‘决策瘫痪’；大脑依赖腹内侧前额叶皮层（vmPFC）与杏仁核协同激活的‘躯体标记’（Somatic Markers）。"
            "过去的经历将特定的情境与生理感受（胃部痉挛、心跳加快、肌肉紧绷或放松）绑定。文案中触动躯体反应的关键词充当‘情绪书签’，"
            "在意识尚未完全理解前，就已经完成了趋利避害的直觉偏好选择。"
        ),
        "neural_regions_activated": "腹内侧前额叶皮层 (vmPFC), 杏仁核 (Amygdala), 前脑岛 (Anterior Insula), 植物神经系统",
        "linguistic_markers": json.dumps({
            "visceral_stress_markers": ["窒息", "冷汗", "紧绷", "疲惫", "掏空", "阵痛", "锁死"],
            "visceral_relief_markers": ["深呼吸", "释怀", "舒展", "回甘", "踏实", "松弛", "卸下"],
            "gut_feeling_anchors": ["心动", "刺痛", "破防", "笃定", "直觉"]
        }, ensure_ascii=False),
        "algorithmic_metric_formula": "Visceral_Tension_Release_Ratio = Count(Relief_Markers) / (Count(Stress_Markers) + 1e-5)",
        "copywriting_application_insight": (
            "文案结构必须设计‘生理应激 $\\rightarrow$ 生理释放’的物理电位差。"
            "前半句精准勾出受众肉身的微观压迫（如‘被闹钟压得喘不过气’），后半句给出生理级卸荷解决方案（‘给疲惫的身体松一松发条’）。"
        ),
        "canonical_benchmark_cases": "杜蕾斯《让每一个冲动都有安全的缓冲》、SK-II《她最后去了相亲角》、每日黑巧《给生活苦味一点巧思》"
    },
    {
        "id": 3,
        "school_name_cn": "乔纳·伯杰 SPEACC 语言转化与行为激活矩阵",
        "school_name_en": "Jonah Berger's SPEACC Influence & Conversion Matrix",
        "key_figures": "Jonah Berger (乔纳·伯杰), Grant Packard, Christopher J. Bryan, Gregory M. Walton",
        "seminal_papers_and_books": json.dumps([
            "Berger, J. (2023). Magic Words: What to Say to Get Your Way. Harper Business.",
            "Bryan, C. J., Walton, G. M., Rogers, T., & Dweck, C. S. (2011). Motivating voter turnout by invoking the self. PNAS, 108(31), 12653-12656.",
            "Packard, G., & Berger, J. (2017). How language shapes word of mouth's impact. Journal of Marketing Research, 54(4), 572-588.",
            "Berger, J., & Packard, G. (2022). Wisdom from words: Marketing insights from text. Marketing Letters, 33(3), 365-376."
        ], ensure_ascii=False),
        "core_psychological_mechanism": (
            "通过大样本 NLP 与行为实验，解码语言影响力的 6 大黄金原子法则 (S.P.E.A.C.C.)：\n"
            "1. Similarity (同理对齐): 使用内群体语言与人称代词匹配；\n"
            "2. Posing Questions (反问设疑): 激活自生成效应 (Self-generation effect)，绕开受众心理防御；\n"
            "3. Emotion (高唤醒情绪): 激发 Awe (敬畏)、Excitement (振奋) 等高生理唤醒词；\n"
            "4. Agency & Identity (身份赋能): 运用‘名词身份锚定’（如‘做一个探索者’）而非动作（‘去探索’），激发自我认同维持机制，转化率高出 16%-30%；\n"
            "5. Confidence (绝对确信): 斩断 hedging（可能、大概），代之以高确信度动词（‘终将’、‘必定’）；\n"
            "6. Concreteness (极度具象): 具象词汇加速心理模拟达 2.8 倍，直接提升信任与购买意向。"
        ),
        "neural_regions_activated": "背外侧前额叶 (dlPFC), 前扣带回 (ACC), 奖赏中枢伏隔核 (NAcc)",
        "linguistic_markers": json.dumps({
            "identity_nouns": ["探索者", "清醒者", "同行人", "破局者", "生活家", "守门人"],
            "high_confidence_cues": ["必定", "终将", "彻底", "毫无疑问", "永远", "绝对"],
            "hedging_taboos": ["可能", "也许", "大概", "某种程度上", "试一试"],
            "self_generation_prompts": ["凭什么", "为什么不", "何不", "难道", "谁说"]
        }, ensure_ascii=False),
        "algorithmic_metric_formula": "SPEACC_Composite = (Identity_Bonus * 0.25 + Concreteness_Score * 0.25 + Confidence_Score * 0.20 + Arousal_Score * 0.15 + Question_Heuristic * 0.15)",
        "copywriting_application_insight": (
            "在口号中把动作升级为‘身份标签’。不要说‘保护你的皮肤’，要说‘做自己肌肤的守门人’；"
            "用反问句代替灌输指令：‘为什么只有周五才配拥有快乐？’直接激发读者自己得出答案。"
        ),
        "canonical_benchmark_cases": "Airbnb《Belong Anywhere (去过，没住过)》、Keep《自律给我自由》、知乎《有问题，就会有答案》"
    },
    {
        "id": 4,
        "school_name_cn": "语言范畴模型与动词具身层级",
        "school_name_en": "Semin & Fiedler's Linguistic Category Model (LCM) & Action Hierarchy",
        "key_figures": "Gün R. Semin, Klaus Fiedler, Luc Schellekens, Peeter Verlegh, Ale Smidts",
        "seminal_papers_and_books": json.dumps([
            "Semin, G. R., & Fiedler, K. (1988). The cognitive functions of linguistic categories in describing persons: Social cognition and language. JPSP, 54(4), 558-568.",
            "Semin, G. R., & Fiedler, K. (1991). The linguistic category model, its bases, applications and range. European Review of Social Psychology, 2(1), 1-30.",
            "Schellekens, G. A., Verlegh, P. W., & Smidts, A. (2010). Language abstraction in word of mouth. Journal of Consumer Research, 37(2), 207-223.",
            "Packard, G., & Berger, J. (2021). How concrete language shapes customer satisfaction. Journal of Consumer Research, 47(5), 787-806."
        ], ensure_ascii=False),
        "core_psychological_mechanism": (
            "语言根据抽象度严格划分为四层阶梯：\n"
            "1. DAV (Descriptive Action Verbs - 描述性行为动词): 如‘拿起’、‘擦拭’、‘奔跑’。最具象，无主观评价，激活神经运动模拟，引发最低的认知防御；\n"
            "2. IAV (Interpretative Action Verbs - 解释性行为动词): 如‘守护’、‘拯救’、‘欺骗’。具备特定含义与评价；\n"
            "3. SV (State Verbs - 心理状态动词): 如‘渴求’、‘崇尚’、‘信赖’。描述心理状态；\n"
            "4. ADJ (Adjectives - 抽象形容词): 如‘卓越的’、‘奢华的’、‘可靠的’。最抽象，缺乏物理证据，易被心智自动归为‘商业夸大’。\n"
            "实证研究证明：在面临购买决策与不确定性时，使用 DAVs 的文案，受众的信任度与满意度高出 ADJs 42% 以上。"
        ),
        "neural_regions_activated": "左侧额下回 (Broca 区), 运动前区 (Premotor Cortex), 颞中回 (MTG)",
        "linguistic_markers": json.dumps({
            "DAV_examples": ["泡", "拧", "涂", "抹", "喝", "踏", "抓", "切", "穿", "敲"],
            "IAV_examples": ["守护", "治愈", "打破", "赋能", "重构", "超越"],
            "SV_examples": ["爱", "恨", "向往", "渴望", "留恋", "崇拜"],
            "ADJ_taboos": ["卓越", "尊贵", "极致", "非凡", "领先", "完美"]
        }, ensure_ascii=False),
        "algorithmic_metric_formula": "LCM_Concreteness_Ratio = (Count(DAV) * 3 + Count(IAV) * 2 + Count(SV) * 1) / (Count(ADJ) * 2 + Total_Verbs + 1e-5)",
        "copywriting_application_insight": (
            "每多用一个形容词，文案就稀释一分力量；每多用一个描述性动词（DAV），文案就多一层肌肉。"
            "用‘小火慢炖 8 小时’干掉‘精心熬制’；用‘三层气囊包裹脚踝’干掉‘绝佳包裹性’。"
        ),
        "canonical_benchmark_cases": "农夫山泉《我们不生产水，我们只是大自然的搬运工》、劳斯莱斯《时速 60 英里时，车内最大噪音来自电子钟》"
    },
    {
        "id": 5,
        "school_name_cn": "元认知加工流畅度与押韵即真理效应",
        "school_name_en": "Metacognitive Processing Fluency & Rhyme-as-Reason Keats Heuristic",
        "key_figures": "Adam L. Alter, Daniel M. Oppenheimer, Rolf Reber, Norbert Schwarz, Matthew S. McGlone",
        "seminal_papers_and_books": json.dumps([
            "Alter, A. L., & Oppenheimer, D. M. (2009). Uniting the tribes of fluency to form a metacognitive theory. Trends in Cognitive Sciences, 13(5), 219-224.",
            "Reber, R., Schwarz, N., & Winkielman, P. (2004). Processing fluency and aesthetic pleasure: Is beauty in the perceiver's processing experience? PSPR, 8(4), 364-382.",
            "McGlone, M. S., & Tofighbakhsh, J. (2000). Birds of a feather flock conjointly (?): Rhyme as reason in aphorisms. Psychological Science, 11(5), 424-428.",
            "Oppenheimer, D. M. (2008). The secret life of fluency. Trends in Cognitive Sciences, 12(6), 237-241."
        ], ensure_ascii=False),
        "core_psychological_mechanism": (
            "人类大脑是崇尚能耗极小化的‘认知吝啬鬼’。当信息具备极高的加工流畅度（音节对称、平仄起伏、声律押韵、发音顺畅）时，"
            "受众主观产生的‘认知轻松感’（Cognitive Ease）会被元认知启发式误判为信息的‘真实性（Truth Effect）’、‘安全性’与‘美学愉悦’。"
            "著名的‘济慈启发式 / 押韵即真理’实验证明：相同语义下，押韵语句（如 'Woes unite foes'）被人们评判为生活真理的概率显著超越散文句（'Woes unite enemies'）。"
        ),
        "neural_regions_activated": "背侧纹状体 (Dorsal Striatum), 眶额皮层 (OFC), 听觉联络皮层",
        "linguistic_markers": json.dumps({
            "phonetic_symmetry_meters": ["4-4", "2-2-3", "3-3", "6-6", "3-3-4"],
            "rhyme_coherence": "十三辙同辙韵母 (尤其是发花、江阳、言前、中东)",
            "cadence_laws": "仄起平收 (前句3/4声，尾句1/2声)"
        }, ensure_ascii=False),
        "algorithmic_metric_formula": "Processing_Fluency_Index = (Symmetry_Score * 0.4 + Rhyme_Hit * 0.3 + Ze_Qi_Ping_Shou * 0.3) * 100",
        "copywriting_application_insight": (
            "口号是念给耳朵听的咒语。必须做到‘读之顺口、听之悦耳、思之省力’。"
            "严格恪守前句仄收吊胃口、尾句平收落尘埃，并利用同辙双押大幅减少心智存储能耗。"
        ),
        "canonical_benchmark_cases": "天猫《理想生活，上天猫》、瓜子二手车《没有中间商赚差价》、步步高《哪里不会点哪里》"
    },
    {
        "id": 6,
        "school_name_cn": "调节聚焦理论与动机语境匹配",
        "school_name_en": "Regulatory Focus Theory (RFT) & Motivational Fit",
        "key_figures": "E. Tory Higgins (托里·希金斯), Jennifer L. Aaker, Angela Y. Lee, Joseph Cesario",
        "seminal_papers_and_books": json.dumps([
            "Higgins, E. T. (1997). Beyond pleasure and pain. American Psychologist, 52(12), 1280-1300.",
            "Higgins, E. T. (1998). Promotion and prevention: Regulatory focus as a motivational principle. Advances in Experimental Social Psychology, 30, 1-46.",
            "Aaker, J. L., & Lee, A. Y. (2001). 'I' seek nurturance and 'we' seek protection: The regulatory focus of dyadic goal pursuits. JCR, 28(1), 33-49.",
            "Cesario, J., Grant, H., & Higgins, E. T. (2004). Regulatory fit and persuasion: Transfer from 'feeling right'. Psychological Science, 15(6), 388-393."
        ], ensure_ascii=False),
        "core_psychological_mechanism": (
            "人类动机由两个独立的自我调节系统引导：\n"
            "1. 促进聚焦 (Promotion Focus): 围绕成长、理想、收获与渴望展开，驱动‘热情策略 (Eagerness)’；\n"
            "2. 预防聚焦 (Prevention Focus): 围绕安全、责任、防范风险与止损展开，驱动‘警戒策略 (Vigilance)’。\n"
            "当广告文案的语汇框架与目标受众当前的调节聚焦状态达成一致时（Regulatory Fit），受众会产生强烈的‘感觉是对的 (Feels Right)’的内隐评价，"
            "该体验会直接转移至产品评价与支付意愿中，提升购买转化达 25%-40%。"
        ),
        "neural_regions_activated": "中脑腹侧被盖区 (VTA), 伏隔核 (Promotion), 杏仁核与背侧前扣带回 (Prevention)",
        "linguistic_markers": json.dumps({
            "promotion_lexicon": ["突破", "解锁", "跃升", "赢得", "渴望", "升级", "无畏", "尽兴", "领跑", "追逐"],
            "prevention_lexicon": ["守住", "底气", "安全", "不负", "踏实", "规避", "兜底", "可靠", "防范", "无忧"]
        }, ensure_ascii=False),
        "algorithmic_metric_formula": "Regulatory_Fit_Alignment = Cosine_Similarity(Copy_Tone_Vector, Audience_State_Vector)",
        "copywriting_application_insight": (
            "面向新锐职场/探险人群，用促进型语汇：‘去发现未曾见过的风景’；"
            "面向高压中产/育儿家庭，用预防型语汇：‘给所爱的人最确定的底气’。严禁在预防型场景中自嗨兜售狂热冒险。"
        ),
        "canonical_benchmark_cases": "沃尔沃《唯爱与生命不可辜负》、宝马《悦动由心 / 纯粹驾驶乐趣》、中国人寿《相知多年，值得托付》"
    },
    {
        "id": 7,
        "school_name_cn": "说话者-倾听者神经耦合与叙事脑共振",
        "school_name_en": "Speaker-Listener Neural Coupling & Storytelling Brain Synchrony",
        "key_figures": "Uri Hasson (尤里·哈松), Greg J. Stephens, Paul J. Zak, Jonathan Gottschall",
        "seminal_papers_and_books": json.dumps([
            "Stephens, G. J., Silbert, L. J., & Hasson, U. (2010). Speaker–listener neural coupling underlies successful communication. PNAS, 107(32), 14425-14430.",
            "Hasson, U., Ghazanfar, A. A., Galantucci, B., et al. (2012). Brain-to-brain coupling: a mechanism for creating and sharing a social world. Trends in Cognitive Sciences, 16(2), 114-121.",
            "Zak, P. J. (2015). Why inspiring stories make us react: The neuroscience of narrative. Cerebrum, 2015, 2.",
            "Gottschall, J. (2012). The Storytelling Animal: How Stories Make Us Human. Houghton Mifflin Harcourt."
        ], ensure_ascii=False),
        "core_psychological_mechanism": (
            "fMRI 脑成像显示：当倾听者听到一个饱含具体细节、冲突与情感波动的真实故事时，倾听者全脑的时空活动模式与叙述者呈现高达 80% 以上的精确同步（Neural Coupling）。"
            "跌宕起伏的叙事张力刺激下丘脑分泌催产素（Oxytocin，建立人际信任）与多巴胺（Dopamine，产生奖赏预期）。"
            "纯逻辑论据会唤醒听众大脑分析批判回路（寻找破绽），而情节具象的故事则直接接管大脑默认网络，使观念不着痕迹地完成移植。"
        ),
        "neural_regions_activated": "默认模式网络 (DMN), 镜像神经元系统 (MNS), 颞顶联合区 (TPJ), 内侧前额叶 (mPFC)",
        "linguistic_markers": json.dumps({
            "temporal_anchors": ["凌晨两点", "雨停的那一刻", "那年夏天", "电梯合上的瞬间", "第十次退回"],
            "dramatic_conflicts": ["然而", "突然", "以为……直到", "终于", "哪怕"],
            "micro_moments": ["松开领带", "擦掉眼泪", "默默熄灭屏幕", "相视一笑"]
        }, ensure_ascii=False),
        "algorithmic_metric_formula": "Narrative_Coupling_Score = (Count(Temporal_Anchors) * 1.5 + Count(Micro_Moments) * 2.0) / Sentences_Count",
        "copywriting_application_insight": (
            "长文案与品牌片解说词的黄金心法：绝不讲抽象道理，只展示‘电影分镜般的微动作’。"
            "‘他站在 26 层的落地窗前，一口冰咖啡顺着喉咙滑下，城市的车流才刚刚苏醒。’用画面接管大脑。"
        ),
        "canonical_benchmark_cases": "胜加《时间的答案》、中国银联《大唐漠北最后一次换粮》、微信支付《红包故事：微信里的中国年》"
    },
    {
        "id": 8,
        "school_name_cn": "VAD 情感三维坐标与高唤醒生理驱动",
        "school_name_en": "Valence, Arousal, Dominance (VAD) & High-Arousal Viral Dynamics",
        "key_figures": "Amy Beth Warriner, Victor Kuperman, Marc Brysbaert, James A. Russell, Katherine L. Milkman",
        "seminal_papers_and_books": json.dumps([
            "Warriner, A. B., Kuperman, V., & Brysbaert, M. (2013). Norms of valence, arousal, and dominance for 13,915 English lemmas. Behavior Research Methods, 45(4), 1191-1207.",
            "Russell, J. A. (1980). A circumplex model of affect. Journal of Personality and Social Psychology, 39(6), 1161-1178.",
            "Berger, J., & Milkman, K. L. (2012). What makes online content viral? Journal of Marketing Research, 49(2), 192-205.",
            "Kuppens, P., Tuerlinckx, F., Russell, J. A., & Barrett, L. F. (2013). The relation between valence and arousal in subjective experience. Psychological Bulletin, 139(4), 917-940."
        ], ensure_ascii=False),
        "core_psychological_mechanism": (
            "人类情绪词汇在大脑中具有严密的三维几何分布：\n"
            "1. Valence (效价): 愉悦度 (-1 到 +1)；\n"
            "2. Arousal (唤醒度): 生理激活度 (0 到 1)。高唤醒（愤怒、敬畏、狂喜、焦虑）激活交感神经，驱动心跳与肌肉蓄力，是社媒‘疯传、点赞、冲动下单’的生理根源；低唤醒（平静、悲伤）抑制行动；\n"
            "3. Dominance (优势度): 掌控感 (0 到 1)。赋予受众支配感（‘由你定义’、‘从容执掌’）可显著缓解现代人的失控焦虑。"
        ),
        "neural_regions_activated": "交感神经系统, 蓝斑核 (Locus Coeruleus - 去甲肾上腺素), 伏隔核",
        "linguistic_markers": json.dumps({
            "high_arousal_positive": ["震撼", "狂欢", "沸腾", "夺目", "燃烧", "呼啸", "惊艳"],
            "high_arousal_negative": ["警惕", "撕裂", "危机", "淘汰", "崩塌", "警报"],
            "high_dominance_empowerment": ["掌控", "主场", "执掌", "自洽", "定义", "从容", "底牌"]
        }, ensure_ascii=False),
        "algorithmic_metric_formula": "Viral_Arousal_Index = (High_Arousal_Count * 2.0 + High_Dominance_Count * 1.5) / Total_Words",
        "copywriting_application_insight": (
            "打造传播爆款时，严禁使用‘温吞、平缓’的低唤醒词汇（如‘还算不错’、‘令人满意’）；"
            "文案要么引发‘惊叹与敬畏’（Awe），要么引发‘夺回掌控权的战栗’（High Dominance），刺激交感神经下达转发与购买指令。"
        ),
        "canonical_benchmark_cases": "耐克《胜者为王 (Am I a Bad Person?)》、红牛《超越极限，挑战不可能》、网易云音乐《看见音乐的力量》"
    },
    {
        "id": 9,
        "school_name_cn": "语音象征学与布巴-奇奇跨模态通感",
        "school_name_en": "Sound Symbolism & The Bouba-Kiki Cross-Modal Synaesthesia",
        "key_figures": "Vilayanur S. Ramachandran, Edward M. Hubbard, Richard R. Klink, Eric A. Yorkston, Geeta Menon",
        "seminal_papers_and_books": json.dumps([
            "Ramachandran, V. S., & Hubbard, E. M. (2001). Synaesthesia—a window into perception, thought and language. Journal of Consciousness Studies, 8(12), 3-34.",
            "Klink, R. R. (2000). Creating brand names with meaning: The use of sound symbolism. Marketing Letters, 11(1), 5-20.",
            "Yorkston, E., & Menon, G. (2004). A sound idea: Phonetic effects of brand names on consumer evaluations. Journal of Consumer Research, 31(1), 43-51.",
            "Spence, C. (2012). Managing sensory expectations using sound: What does sound symbolism tell us about the meaning of words and the look of brands? Journal of Brand Management, 19(9), 778-796."
        ], ensure_ascii=False),
        "core_psychological_mechanism": (
            "跨越所有人类语言与文化，95% 以上的人会将尖锐棱角图形指认为‘Kiki’，将圆润柔软图形指认为‘Bouba’。\n"
            "发音器官的物理运动（舌尖前顶、声门爆破 vs 双唇圆拢、咽腔共鸣）在大脑角回（Angular Gyrus）诱发多模态神经联觉：\n"
            "- 前高元音 [i, e] + 清塞音 [k, t, p]: 神经绑定‘微小、轻盈、锋利、极速、冰凉、现代感’；\n"
            "- 后低元音 [u, o, a] + 浊音/鼻音 [b, d, g, m, n]: 神经绑定‘宏大、厚重、温暖、圆润、包容、奢华’。\n"
            "当品牌名与文案的音系特征与产品属性达成‘音义一致（Phonetic Congruity）’时，心智接受速度提高数倍。"
        ),
        "neural_regions_activated": "角回 (Angular Gyrus), 听觉-视觉联络皮层, 顶叶内侧沟",
        "linguistic_markers": json.dumps({
            "kiki_sharp_tokens": ["快", "破", "劈", "特", "克", "尖", "极", "精", "晶", "切"],
            "bouba_round_tokens": ["润", "暖", "绵", "梦", "浓", "丰", "满", "漫", "融", "醇"]
        }, ensure_ascii=False),
        "algorithmic_metric_formula": "Phonetic_Congruity_Score = Match(Target_Attribute_Vibe, Phonetic_Feature_Vector)",
        "copywriting_application_insight": (
            "轻薄数码、运动竞速口号，多用清脆齿音与前元音（如‘一瞬、击穿、极光’）；"
            "个护母婴、高端奶酪、深度睡眠文案，多用圆唇后元音与鼻音（如‘温润、柔棉、如梦、沉香’）。"
        ),
        "canonical_benchmark_cases": "Kindle (点燃/轻巧)、Dove (多芬/温和飞羽)、Swiffer (快速拂过)、Rimowa (坚固沉稳)"
    },
    {
        "id": 10,
        "school_name_cn": "心智无意识“因为”启发式与前景理论损失厌恶",
        "school_name_en": "Mindlessness 'Because' Heuristic & Prospect Theory Loss Aversion",
        "key_figures": "Ellen J. Langer, Amos Tversky, Daniel Kahneman, Irwin P. Levin",
        "seminal_papers_and_books": json.dumps([
            "Langer, E. J., Blank, A., & Chanowitz, B. (1978). The mindlessness of ostensibly thoughtful action: The role of 'placebic' information in communicative interaction. JPSP, 36(6), 635-642.",
            "Tversky, A., & Kahneman, D. (1981). The framing of decisions and the psychology of choice. Science, 211(4481), 453-458.",
            "Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. Econometrica, 47(2), 263-291.",
            "Levin, I. P., Schneider, S. L., & Gaeth, G. J. (1998). All frames are not created equal: A typology and critical analysis of framing effects. OBHDP, 76(2), 149-188."
        ], ensure_ascii=False),
        "core_psychological_mechanism": (
            "人类认知两大经典偏误法则：\n"
            "1. 兰格‘因为’启发式 (The 'Because' Heuristic): 大脑对因果连接词存在‘自动驾驶式顺从’。哪怕连接词后跟随的是无逻辑废话，服从率也从 60% 跃升至 93% 以上；\n"
            "2. 前景理论损失厌恶 (Loss Aversion Framing): 人们对损失的敏感度是对等收益的 2.1-2.5 倍（S 型价值函数）。\n"
            "强调‘如果不做，你将错失什么’比单纯强调‘你可以得到什么’，唤醒的前额叶背侧警戒电位与行动紧迫感高出一倍以上。"
        ),
        "neural_regions_activated": "背外侧前额叶 (dlPFC), 岛叶前部 (Pain & Risk), 尾状核",
        "linguistic_markers": json.dumps({
            "causal_heuristic_triggers": ["因为", "正因如此", "之所以……是为了", "所以", "才能"],
            "loss_aversion_frames": ["别让……偷走", "别等失去才……", "少走弯路", "不可逆", "代价", "遗憾"]
        }, ensure_ascii=False),
        "algorithmic_metric_formula": "Causal_Loss_Impact_Index = (Count(Causal_Triggers) * 1.5 + Count(Loss_Frames) * 2.0) / Sentences_Count",
        "copywriting_application_insight": (
            "在品牌主张中务必给出‘无可反驳的因果锚点’与‘不可承受的痛点代价’。"
            "‘之所以苛刻，是因为对生命没有侥幸。’‘别让这座城市的繁华，掩盖了你眼里逐渐熄灭的光。’"
        ),
        "canonical_benchmark_cases": "欧莱雅《因为你值得 (Because You're Worth It)》、联邦快递《当它绝对、必须隔夜送达》、腾讯公益《小朋友画廊》"
    }
]


def init_db(db_path: Path):
    """Create table psycholinguistic_activation_canon and ingest data."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS psycholinguistic_activation_canon (
            id INTEGER PRIMARY KEY,
            school_name_cn TEXT NOT NULL,
            school_name_en TEXT NOT NULL,
            key_figures TEXT NOT NULL,
            seminal_papers_and_books TEXT NOT NULL,
            core_psychological_mechanism TEXT NOT NULL,
            neural_regions_activated TEXT NOT NULL,
            linguistic_markers TEXT NOT NULL,
            algorithmic_metric_formula TEXT NOT NULL,
            copywriting_application_insight TEXT NOT NULL,
            canonical_benchmark_cases TEXT NOT NULL
        )
    """)

    cursor.execute("DELETE FROM psycholinguistic_activation_canon")

    for item in PSYCHOLINGUISTIC_CANON:
        cursor.execute("""
            INSERT INTO psycholinguistic_activation_canon (
                id, school_name_cn, school_name_en, key_figures,
                seminal_papers_and_books, core_psychological_mechanism,
                neural_regions_activated, linguistic_markers,
                algorithmic_metric_formula, copywriting_application_insight,
                canonical_benchmark_cases
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["id"],
            item["school_name_cn"],
            item["school_name_en"],
            item["key_figures"],
            item["seminal_papers_and_books"],
            item["core_psychological_mechanism"],
            item["neural_regions_activated"],
            item["linguistic_markers"],
            item["algorithmic_metric_formula"],
            item["copywriting_application_insight"],
            item["canonical_benchmark_cases"]
        ))

    conn.commit()
    conn.close()
    print(f"✅ Ingested {len(PSYCHOLINGUISTIC_CANON)} psycholinguistic activation schools into 'psycholinguistic_activation_canon'.")


def export_json(output_path: Path):
    """Export dataset to JSON format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(PSYCHOLINGUISTIC_CANON, f, ensure_ascii=False, indent=2)
    print(f"✅ Exported JSON dataset to: {output_path}")


if __name__ == "__main__":
    db_file = PROJECT_ROOT / "via54_kb.db"
    json_file = PROJECT_ROOT / "knowledge" / "psycholinguistic_activation_canon.json"
    init_db(db_file)
    export_json(json_file)
