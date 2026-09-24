#!/usr/bin/env python3
"""
build_master_writers_triplet_kb.py
Builds Master Writers Triplet Knowledge Base with 3 independent, cleanly indexed tables:
  1. master_writers_originals: Original foreign texts, chapter extracts, philosophy & themes
  2. master_writers_translations: Canonical translations by legendary masters (王道乾, 朱生豪, 余光中, 巫宁坤, 傅雷, 郑振铎, 周煦良, 舒昌善, 王永年, 叶廷芳, 杜小真, 柳鸣九等), translation school & style aesthetics, translator commentaries
  3. master_writers_golden_quotes: Canonical epigrams, paradox & rhetorical mechanisms, theme tags, and modern advertising/branding application blueprints.

Focuses heavily on Oscar Wilde while thoroughly covering Shakespeare, Duras, Fitzgerald, Hemingway, Camus, Maugham, Zweig, Borges, Tagore, Kafka.
"""

import sys
import os
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── 1. 原本库 (Master Writers Originals) ──
ORIGINALS_DATA: List[Dict[str, Any]] = [
    # ── 奥斯卡·王尔德 (Oscar Wilde) ──
    {
        "id": 1,
        "writer_name_en": "Oscar Wilde",
        "writer_name_cn": "奥斯卡·王尔德",
        "work_title_en": "The Picture of Dorian Gray",
        "work_title_cn": "道连·格雷的画像",
        "source_language": "English",
        "genre": "唯美主义哲理小说",
        "original_text_extract": """The Preface:
The artist is the creator of beautiful things. To reveal art and conceal the artist is art's aim.
The critic is he who can translate into another manner or a new material his impression of beautiful things.
There is no such thing as a moral or an immoral book. Books are well written, or badly written. That is all.
No artist has ethical sympathies. An ethical sympathy in an artist is an unpardonable mannerism of style.
All art is quite useless.

Chapter 2:
"I can resist everything except temptation."
"The only way to get rid of a temptation is to yield to it. Resist it, and your soul grows sick with longing for the things it has forbidden to itself, with desire for what its monstrous laws have made monstrous and unlawful."
"Nowadays people know the price of everything and the value of nothing." """,
        "themes_and_philosophy": "唯美主义宣言，主张‘为艺术而艺术 (Art for Art's sake)’。将审美体验置于传统维多利亚时代道德教条之上，深刻剖析欲望、灵魂异化、永恒青春与肉体堕落的宿命对决。"
    },
    {
        "id": 2,
        "writer_name_en": "Oscar Wilde",
        "writer_name_cn": "奥斯卡·王尔德",
        "work_title_en": "Lady Windermere's Fan",
        "work_title_cn": "温夫人的扇子",
        "source_language": "English",
        "genre": "唯美主义世态喜剧",
        "original_text_extract": """Act III:
Lord Darlington: "We are all in the gutter, but some of us are looking at the stars."
Cecil Graham: "What is a cynic?"
Lord Darlington: "A man who knows the price of everything and the value of nothing."
Cecil Graham: "And a sentimentalist, my dear Darlington?"
Lord Darlington: "A man who sees an absurd value in everything, and doesn't know the market price of any single thing."
Dumby: "Experience is simply the name we give our mistakes."
Lord Darlington: "There are only two tragedies in life: one is not getting what one wants, and the other is getting it." """,
        "themes_and_philosophy": "维多利亚时代上流社会假面撕裂，以极其锋利机智的机锋对话击破道德洁癖与虚伪，展现卑污现实中未熄灭的理想主义星光与母爱救赎。"
    },
    {
        "id": 3,
        "writer_name_en": "Oscar Wilde",
        "writer_name_cn": "奥斯卡·王尔德",
        "work_title_en": "The Importance of Being Earnest",
        "work_title_cn": "不可儿戏 (认真的重要性)",
        "source_language": "English",
        "genre": "唯美主义世态荒诞喜剧",
        "original_text_extract": """Act I:
Algernon: "I may mention that I have always suspected you of being a confirmed and secret Bunburyist."
Jack: "It is a very ungentlemanly thing to read a private cigarette case."
Algernon: "It is absurd to divide people into good and bad. People are either charming or tedious. I take the side of charming people, and there is no one among them, but yourself, whom I cannot persuade to do anything."
Algernon: "The truth is rarely pure and never simple. Modern life would be very tedious if it were either, and modern literature a complete impossibility!" """,
        "themes_and_philosophy": "王尔德喜剧艺术最高峰，‘严肃地对待一切轻浮之事，轻浮地对待一切严肃之事’。彻底解构身份认同、婚姻契约与道德教条，以纯粹的形式美与语言幽默超越意义本身。"
    },
    {
        "id": 4,
        "writer_name_en": "Oscar Wilde",
        "writer_name_cn": "奥斯卡·王尔德",
        "work_title_en": "An Ideal Husband",
        "work_title_cn": "理想丈夫",
        "source_language": "English",
        "genre": "唯美主义世态喜剧",
        "original_text_extract": """Act III:
Lord Goring: "To love oneself is the beginning of a lifelong romance."
Mrs. Cheveley: "Morality is simply the attitude we adopt towards people whom we personally dislike."
Lord Goring: "Fashion is what one wears oneself. What is unfashionable is what other people wear."
Lord Goring: "Women have a wonderful instinct about things. They can discover everything except the obvious."
Sir Robert Chiltern: "When men love us, they love us for our credit; when women love us, they forgive us our sins." """,
        "themes_and_philosophy": "探讨完美假象与人性幽微的宽恕，确立自爱与个人独立主权为最高伦理，揭露世俗政客与道德法官的双重标准。"
    },
    {
        "id": 5,
        "writer_name_en": "Oscar Wilde",
        "writer_name_cn": "奥斯卡·王尔德",
        "work_title_en": "De Profundis",
        "work_title_cn": "自深深处 (狱中记)",
        "source_language": "English",
        "genre": "书信体自传散文 / 忏悔录",
        "original_text_extract": """Suffering is one very long moment. We cannot divide it by seasons. We can only record its moods, and chronicle their return.
Where there is sorrow there is holy ground. Some day people will realise what that means. They will know nothing about life till they do.
Behind sorrow there is always sorrow. A wound that flinches is a wound that cries for healing.
I have got to make everything that has happened to me good for me. The plank bed, the loathsome food, the hard ropes shredded into oakum until one's fingertips grow dull with pain... the silence, the solitude, the shame—each and all of these things I have to transform into a spiritual experience.""",
        "themes_and_philosophy": "王尔德入狱后向波西写就的心灵巨制。超越了唯美主义的表面欢愉，进入受难与苦难哲学的圣域，把苦难升华为灵魂的再生仪式。"
    },
    {
        "id": 6,
        "writer_name_en": "Oscar Wilde",
        "writer_name_cn": "奥斯卡·王尔德",
        "work_title_en": "The Decay of Lying",
        "work_title_cn": "谎言的衰落",
        "source_language": "English",
        "genre": "文艺对话录 / 批评散文",
        "original_text_extract": """Vivian: "Life imitates Art far more than Art imitates Life. This results not merely from Life's imitative instinct, but from the fact that the self-conscious aim of Life is to find expression, and that Art offers it certain beautiful forms through which it may realise that energy."
Vivian: "Lying, the telling of beautiful untrue things, is the proper aim of Art."
Vivian: "Things are because we see them, and what we see, and how we see it, depends on the Arts that have influenced us. To look at a thing is very different from seeing a thing." """,
        "themes_and_philosophy": "颠覆亚里士多德‘艺术模仿自然’的千古传统，提出革命性论断‘生活模仿艺术’；艺术并非复制现实，而是为浑浊的生活赋予美学形式与灵魂。"
    },
    {
        "id": 7,
        "writer_name_en": "Oscar Wilde",
        "writer_name_cn": "奥斯卡·王尔德",
        "work_title_en": "The Soul of Man under Socialism",
        "writer_name_cn": "奥斯卡·王尔德",
        "work_title_cn": "社会主义下人的灵魂",
        "source_language": "English",
        "genre": "政治哲学与个人主义随笔",
        "original_text_extract": """Selfishness is not living as one wishes to live, it is asking others to live as one wishes to live. And unselfishness is letting other people's lives alone, not interfering with them.
Selfishness always aims at creating around it an absolute uniformity of type. Unselfishness recognises infinite variety of type as a delightful thing, accepts it, acquiesces in it, enjoys it.
A map of the world that does not include Utopia is not worth even glancing at, for it leaves out the one country at which Humanity is always landing.""",
        "themes_and_philosophy": "王尔德对极端个人主义与真正自由的哲学阐述，重新厘定自私与无私的边界，反对一切泯灭个性的标准化流水线控制，呼唤乌托邦理想。"
    },

    # ── 威廉·莎士比亚 (William Shakespeare) ──
    {
        "id": 8,
        "writer_name_en": "William Shakespeare",
        "writer_name_cn": "威廉·莎士比亚",
        "work_title_en": "Hamlet",
        "work_title_cn": "哈姆雷特",
        "source_language": "English",
        "genre": "人文主义悲剧",
        "original_text_extract": """Act III, Scene 1:
To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles
And by opposing end them. To die—to sleep,
No more; and by a sleep to say we end
The heart-ache and the thousand natural shocks
That flesh is heir to: 'tis a consummation
Devoutly to be wish'd.

Act II, Scene 2:
What a piece of work is a man! How noble in reason! how infinite in faculties! in form and moving how express and admirable! in action how like an angel! in apprehension how like a god! the beauty of the world! the paragon of animals!""",
        "themes_and_philosophy": "文艺复兴时期人类自我意识觉醒的终极哲学命题，理性与行动的撕扯，生命脆弱与宇宙无限尊严的交响。"
    },
    {
        "id": 9,
        "writer_name_en": "William Shakespeare",
        "writer_name_cn": "威廉·莎士比亚",
        "work_title_en": "Romeo and Juliet",
        "work_title_cn": "罗密欧与朱丽叶",
        "source_language": "English",
        "genre": "抒情悲剧",
        "original_text_extract": """Act II, Scene 2:
Juliet: "O Romeo, Romeo! wherefore art thou Romeo? Deny thy father and refuse thy name; Or, if thou wilt not, be but sworn my love, And I'll no longer be a Capulet.
'Tis but thy name that is my enemy; Thou art thyself, though not a Montague. What's in a name? that which we call a rose By any other word would smell as sweet."

Act II, Scene 6:
Friar Laurence: "These violent delights have violent ends, And in their triumph die, like fire and powder, Which, as they kiss, consume." """,
        "themes_and_philosophy": "纯洁热烈的人性之爱对抗古老家族宿怨，符号标签与本体价值的剥离，狂暴激情与毁灭命运的共生。"
    },
    {
        "id": 10,
        "writer_name_en": "William Shakespeare",
        "writer_name_cn": "威廉·莎士比亚",
        "work_title_en": "Sonnet 18",
        "work_title_cn": "十四行诗·第18首",
        "source_language": "English",
        "genre": "商籁体抒情诗",
        "original_text_extract": """Shall I compare thee to a summer's day?
Thou art more lovely and more temperate:
Rough winds do shake the darling buds of May,
And summer's lease hath all too short a date:
...
But thy eternal summer shall not fade,
Nor lose possession of that fair thou ow'st;
Nor shall death brag thou wander'st in his shade,
When in eternal lines to time thou grow'st:
So long as men can breathe, or eyes can see,
So long lives this, and this gives life to thee.""",
        "themes_and_philosophy": "诗歌艺术战胜时间与死亡的永恒性信仰。世俗夏日转瞬即逝，唯有艺术语言赋予生命不可磨灭的永恒不朽。"
    },

    # ── 玛格丽特·杜拉斯 (Marguerite Duras) ──
    {
        "id": 11,
        "writer_name_en": "Marguerite Duras",
        "writer_name_cn": "玛格丽特·杜拉斯",
        "work_title_en": "L'Amant (The Lover)",
        "work_title_cn": "情人",
        "source_language": "French",
        "genre": "自传体现代主义小说",
        "original_text_extract": """Un jour, j'étais âgée déjà, dans le hall d'un lieu public, un homme est venu vers moi. Il s'est fait connaître et il m'a dit : « Je vous connais depuis toujours. Tout le monde dit que vous étiez belle lorsque vous étiez jeune, je suis venu pour vous dire que pour moi je vous trouve plus belle maintenant que lorsque vous étiez jeune, j'aimais moins votre visage de jeune femme que celui que vous avez maintenant, dévasté. »

Très vite dans ma vie il a été trop tard. À dix-huit ans il était déjà trop tard. Entre dix-huit ans et vingt-cinq ans mon visage est parti dans une direction imprévue. À dix-huit ans j'ai vieilli.""",
        "themes_and_philosophy": "时间、衰老、欲望与绝望之爱。颠覆传统对青春肉体胶原蛋白的世俗崇拜，将岁月摧残的面容升华为带有灵魂风霜与宿命美感的艺术品。"
    },

    # ── 弗·司各特·菲茨杰拉德 (F. Scott Fitzgerald) ──
    {
        "id": 12,
        "writer_name_en": "F. Scott Fitzgerald",
        "writer_name_cn": "弗·司各特·菲茨杰拉德",
        "work_title_en": "The Great Gatsby",
        "work_title_cn": "了不起的盖茨比",
        "source_language": "English",
        "genre": "爵士时代现实主义与象征主义小说",
        "original_text_extract": """Gatsby believed in the green light, the orgastic future that year by year recedes before us. It eluded us then, but that’s no matter—tomorrow we will run faster, stretch out our arms farther. . . . And one fine morning——
So we beat on, boats against the current, borne back ceaselessly into the past.

In my younger and more vulnerable years my father gave me some advice that I’ve been turning over in my mind ever since.
"Whenever you feel like criticizing any one," he told me, "just remember that all the people in this world haven't had the advantages that you've had." """,
        "themes_and_philosophy": "美国梦的幻灭与人类对不可追回之过往的执着悲歌。码头尽头那一抹微弱的绿灯，是人类向着不可抵达之彼岸永远奋力泅渡的终极隐喻。"
    },

    # ── 欧内斯特·海明威 (Ernest Hemingway) ──
    {
        "id": 13,
        "writer_name_en": "Ernest Hemingway",
        "writer_name_cn": "欧内斯特·海明威",
        "work_title_en": "The Old Man and the Sea",
        "work_title_cn": "老人与海",
        "source_language": "English",
        "genre": "硬汉文学中篇小说",
        "original_text_extract": """He was an old man who fished alone in a skiff in the Gulf Stream and he had gone eighty-four days now without taking a fish.
"Man is not made for defeat," he said. "A man can be destroyed but not defeated."
"It is silly not to hope, he thought. Besides I believe it is a sin."
"Now is no time to think of what you do not have. Think of what you can do with what there is." """,
        "themes_and_philosophy": "海明威‘冰山理论’与硬汉哲学集大成者。肉体可以被大海与鲨鱼群撕碎摧毁，但人类不屈的尊严与意志绝不能被打败。"
    },
    {
        "id": 14,
        "writer_name_en": "Ernest Hemingway",
        "writer_name_cn": "欧内斯特·海明威",
        "work_title_en": "A Moveable Feast",
        "work_title_cn": "流动的盛宴",
        "source_language": "English",
        "genre": "回忆录散文",
        "original_text_extract": """If you are lucky enough to have lived in Paris as a young man, then wherever you go for the rest of your life, it stays with you, for Paris is a moveable feast.
There is never any ending to Paris and the memory of each person who has lived in it differs from that of any other. We always returned to it no matter who we were or how it was changed or with what difficulties, or ease, it could be reached.""",
        "themes_and_philosophy": "青年时代精神养分对一生的浸润与馈赠。将一座城市化为终身随身携带的精神盛宴，照亮困顿平庸的漫漫余生。"
    },

    # ── 阿尔贝·加缪 (Albert Camus) ──
    {
        "id": 15,
        "writer_name_en": "Albert Camus",
        "writer_name_cn": "阿尔贝·加缪",
        "work_title_en": "L'Étranger (The Stranger)",
        "work_title_cn": "局外人",
        "source_language": "French",
        "genre": "存在主义与荒诞派小说",
        "original_text_extract": """Aujourd'hui, maman est morte. Ou peut-être hier, je ne sais pas. J'ai reçu un télégramme de l'asile : « Mère décédée. Enterrement demain. Sentiments distingués. » Cela ne veut rien dire. C'était peut-être hier.
Pour que tout soit consommé, pour que je me sente moins seul, il me restait à souhaiter qu'il y ait beaucoup de spectateurs le jour de mon exécution et qu'ils m'accueillent avec des cris de haine.""",
        "themes_and_philosophy": "世界的荒谬与拒绝伪善的纯粹真实。主人公默尔索因拒绝在母亲葬礼上表演悲伤而被社会合谋处死，以冷峻的诚实撕碎整个文明的道德伪善。"
    },
    {
        "id": 16,
        "writer_name_en": "Albert Camus",
        "writer_name_cn": "阿尔贝·加缪",
        "work_title_en": "Le Mythe de Sisyphe",
        "work_title_cn": "西西弗神话",
        "source_language": "French",
        "genre": "哲学随笔",
        "original_text_extract": """Il n'y a qu'un problème philosophique vraiment sérieux : c'est le suicide. Juger que la vie vaut ou ne vaut pas la peine d'être vécue, c'est répondre à la question fondamentale de la philosophie.
La lutte elle-même vers les sommets suffit à remplir un cœur d'homme. Il faut imaginer Sisyphe heureux.""",
        "themes_and_philosophy": "直面荒诞并在荒诞中英勇反抗。推巨石上山虽永无止境且毫无外在意义，但推石上山本身就足以充实人心，反抗赋予生命最高尊严。"
    },

    # ── 威廉·萨默塞特·毛姆 (W. Somerset Maugham) ──
    {
        "id": 17,
        "writer_name_en": "W. Somerset Maugham",
        "writer_name_cn": "威廉·萨默塞特·毛姆",
        "work_title_en": "The Moon and Sixpence",
        "work_title_cn": "月亮与六便士",
        "source_language": "English",
        "genre": "传记体哲理小说",
        "original_text_extract": """I wanted to tell Strickland that it was an absurd adventure, that he was throwing away a substantial position and a comfortable home for a phantom.
"I tell you I've got to paint," he repeated.
"I can't help myself. When a man falls into the water it doesn't matter how he swims, well or badly: he's got to get out or else he'll drown."
He looked at the moon, and then down at the sixpence lying in the gutter.""",
        "themes_and_philosophy": "理想天体（月亮）与世俗琐屑（六便士）的永恒决裂。对艺术纯粹激情的狂暴臣服，哪怕抛弃中产阶级安稳体面，也绝不妥协。"
    },
    {
        "id": 18,
        "writer_name_en": "W. Somerset Maugham",
        "writer_name_cn": "威廉·萨默塞特·毛姆",
        "work_title_en": "The Razor's Edge",
        "work_title_cn": "刀锋",
        "source_language": "English",
        "genre": "哲理小说",
        "original_text_extract": """The sharp edge of a razor is difficult to pass over; thus the wise say the path to Salvation is hard.
"I want to make up my mind whether God is or God is not. I want to find out why evil exists. I want to know whether I have an immortal soul or whether when I die it's the end."
Larry: "I've been thinking about what you said. I don't want to buy things, and I don't want to make money. I want to loaf." """,
        "themes_and_philosophy": "借《迦托奥义书》箴言‘一把刀的锋刃很难越过；得救之道是困难的’，探讨在物质繁华与世界大战创伤之后，人类对精神解脱与终极真理的求索。"
    },

    # ── 斯蒂芬·茨威格 (Stefan Zweig) ──
    {
        "id": 19,
        "writer_name_en": "Stefan Zweig",
        "writer_name_cn": "斯蒂芬·茨威格",
        "work_title_en": "Sternstunden der Menschheit",
        "work_title_cn": "人类群星闪耀时",
        "source_language": "German",
        "genre": "历史特写传记",
        "original_text_extract": """Solche dramatisch konzentrierten, solche schicksalsträchtigen Stunden, in denen eine zeitüberdauernde Entscheidung auf ein einziges Datum, eine einzige Stunde und oft nur eine Minute zusammengedrängt ist, sind selten im Leben eines Einzelnen und selten im Laufe der Geschichte.
Ein größeres Glück kann einem Menschen nicht zuteilwerden, als seine Lebensaufgabe in der Mitte des Lebens zu finden.""",
        "themes_and_philosophy": "历史长河中决定命运的微小时刻与天才意志的爆发。平庸时代如漫长暗夜，唯有少数决定性瞬间，人类意志如群星般照亮整个苍穹。"
    },
    {
        "id": 20,
        "writer_name_en": "Stefan Zweig",
        "writer_name_cn": "斯蒂芬·茨威格",
        "work_title_en": "Brief einer Unbekannten",
        "work_title_cn": "一个陌生女人的来信",
        "source_language": "German",
        "genre": "心理分析小说",
        "original_text_extract": """Dir, der du mich nie gekannt hast...
Mein Kind ist gestern gestorben—drei Tage lang habe ich mit dem Tode um dies zarte, kleine Leben gerungen... Jetzt habe ich nur mehr dich auf der Welt, nur dich, der du von mir nichts weißt, der du indessen ahnungslos spielst oder mit Dingen und Menschen tändelst, dich, der du mich nie gekannt und den ich immer geliebt.
Es gibt nichts Schrecklicheres als das Alleinsein unter Menschen.""",
        "themes_and_philosophy": "单向度极致献祭之爱。毫无功利回报指望的纯粹痴绝，将个体的全部生命热量投掷在一个浑然不觉的客体之上，展现惊心动魄的心理深渊。"
    },

    # ── 豪尔赫·路易斯·博尔赫斯 (Jorge Luis Borges) ──
    {
        "id": 21,
        "writer_name_en": "Jorge Luis Borges",
        "writer_name_cn": "豪尔赫·路易斯·博尔赫斯",
        "work_title_en": "El jardín de senderos que se bifurcan",
        "work_title_cn": "小径分岔的花园",
        "source_language": "Spanish",
        "genre": "形而上学哲学小说",
        "original_text_extract": """El jardín de senderos que se bifurcan es una imagen incompleta, pero no falsa, del universo tal como lo concebía Ts'ui Pên. A diferencia de Newton y de Schopenhauer, su antepasado no creía en un tiempo uniforme, absoluto. Creía en infinitas series de tiempos, en una red creciente y vertiginosa de tiempos divergentes, convergentes y paralelos.
El tiempo se bifurca perpetuamente hacia innumerables futuros.""",
        "themes_and_philosophy": "迷宫、时间分支与平行宇宙的哲学寓言。时间并非单向奔流的河水，而是无限分岔的网络，每一个选择都诞生出一个崭新的宇宙。"
    },
    {
        "id": 22,
        "writer_name_en": "Jorge Luis Borges",
        "writer_name_cn": "豪尔赫·路易斯·博尔赫斯",
        "work_title_en": "El Aleph",
        "work_title_cn": "阿莱夫",
        "source_language": "Spanish",
        "genre": "奇幻哲学短篇",
        "original_text_extract": """Vi el Aleph, desde todos los puntos, vi en el Aleph la tierra, y en la tierra otra vez el Aleph y en el Aleph la tierra... Vi un laberinto roto (era Londres), vi interminables ojos inmediatos escrutándose en mí como en un espejo, vi todos los espejos del planeta y ninguno me reflejó...
Sentí infinita veneración, infinita lástima.""",
        "themes_and_philosophy": "全知全视与人类有限语言的悖论。空间中汇聚整个宇宙所有点的那一点（阿莱夫），象征着人类对全知维度的无限向往与面对无限时的震颤怜悯。"
    },

    # ── 拉宾德拉纳特·泰戈尔 (Rabindranath Tagore) ──
    {
        "id": 23,
        "writer_name_en": "Rabindranath Tagore",
        "writer_name_cn": "拉宾德拉纳特·泰戈尔",
        "work_title_en": "Stray Birds",
        "work_title_cn": "飞鸟集",
        "source_language": "Bengali/English",
        "genre": "哲理格言抒情诗",
        "original_text_extract": """Stray birds of summer come to my window to sing and fly away. And yellow leaves of autumn, which have no songs, flutter and fall there with a sign.
Let life be beautiful like summer flowers and death like autumn leaves.
If you shed tears when you miss the sun, you also miss the stars.
The world puts off its mask of vastness to its lover. It becomes small as one song, as one kiss of the eternal.""",
        "themes_and_philosophy": "人与自然、微尘与宇宙的神秘合一。以极其轻盈纯真的短句，点破生命生死与爱之庄严，具有直通万物有灵的博大慈悲。"
    },

    # ── 弗朗茨·卡夫卡 (Franz Kafka) ──
    {
        "id": 24,
        "writer_name_en": "Franz Kafka",
        "writer_name_cn": "弗朗茨·卡夫卡",
        "work_title_en": "Die Verwandlung (The Metamorphosis)",
        "work_title_cn": "变形记",
        "source_language": "German",
        "genre": "表现主义荒诞中篇小说",
        "original_text_extract": """Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheuren Ungeziefer verwandelt.
Er lag auf seinem panzerartig harten Rücken und sah, wenn er den Kopf ein wenig hob, seinen gewölbten, braunen, von bogenförmigen Versteifungen geteilten Bauch...
„Was ist mit mir geschehen?“, dachte er. Es war kein Traum.""",
        "themes_and_philosophy": "现代工业社会异化与工具人困境的终极预言。当人失去作为职场螺丝钉的生产力价值，即刻沦为家庭与社会弃之如敝履的‘害虫’。"
    }
]


# ── 2. 译本库 (Master Writers Translations) ──
TRANSLATIONS_DATA: List[Dict[str, Any]] = [
    # 王尔德
    {
        "id": 1,
        "original_id": 1,
        "work_title_cn": "道连·格雷的画像",
        "translator": "荣如德",
        "translation_text": """序言：
艺术家是美的事物的创造者。暴露艺术而隐匿艺术家，乃是艺术的宗旨。
批评家能够把对美的事物的印象，转化为另一种方式或新的材料。
没有所谓的道德的书或不道德的书。书要么写得好，要么写得糟。仅此而已。
艺术家没有任何伦理上的好恶。伦理上的好恶在艺术家身上乃是一种不可原谅的风格造作。
一切艺术都是毫无用处的。

第二章：
“我能抗拒一切，除了诱惑。”
“摆脱诱惑的唯一方法，是向它屈服。倘若抵制它，你的灵魂便会因渴望它禁止自己得到的东西而染上相思之疾，因向往它可怕的法则宣布为怪物和非法的东西而变得病态。”
“如今的人知道所有东西的价钱，却对它们的价值一无所知。”""",
        "translation_school_and_style": "荣如德严谨博雅的文风，词汇考究典雅，精准传达出王尔德冷峻、骄傲且充满英伦贵族机锋的唯美调性。",
        "translator_commentary": "荣如德指出王尔德文字表面的‘轻薄玩世’实则是对维多利亚伪善道德的宣战。译文在‘价钱’与‘价值’、‘诱惑’与‘屈服’的中文对应上做到了入骨三分。"
    },
    {
        "id": 2,
        "original_id": 2,
        "work_title_cn": "温夫人的扇子",
        "translator": "余光中",
        "translation_text": """第三幕：
达林顿勋爵：“我们都在阴沟里，但仍有人仰望星空。”
塞西尔·格雷厄姆：“什么是犬儒主义者？”
达林顿勋爵：“一个知道一切东西的市价，却对它们的价值一无所知的人。”
塞西尔：“那么伤感主义者呢，亲爱的达林顿？”
达林顿：“一个在所有事物中看到荒谬价值，却不知道其中任何一件的市场公道价的人。”
丹比：“经验，不过是每个人给自己犯过的错误起的名字。”
达林顿勋爵：“生活中只有两种悲剧：一种是没有得到想要的东西，另一种是得到了它。”""",
        "translation_school_and_style": "余光中先生戏剧翻译神品，善用汉语四字成语与短促有力的句式，既保留王尔德英文的脆响与机智，又赋予汉语独有的朗朗上口节奏。",
        "translator_commentary": "余光中自豪于王尔德戏剧的引介，称王尔德台词‘句句带刺，字字生光’。余译特意强化了对仗感与剧场听觉穿透力，使‘仰望星空’与‘阴沟’成为华语界传诵百年的对偶金句。"
    },
    {
        "id": 3,
        "original_id": 3,
        "work_title_cn": "不可儿戏",
        "translator": "余光中",
        "translation_text": """第一幕：
阿尔及侬：“把人分成好人和坏人是荒谬的。人要么迷人，要么乏味。我站在迷人这一边，而在迷人的人当中，除了你之外，没有一个人是我劝不动的。”
阿尔及侬：“真相很少纯粹，而且绝不简单。现代生活如果既纯粹又简单，就会变得枯燥无味；而现代文学也就完全不可能存在了！”""",
        "translation_school_and_style": "余光中译本打破字面对译，将‘Earnest’与人名‘Ernest’的双关谐音化为汉语《不可儿戏》，行文机巧跳跃，剧场效果拉满。",
        "translator_commentary": "余光中认为《不可儿戏》是英语世态喜剧最纯净的杰作，毫无说教意图，纯靠语言本身的杂耍与荒谬正论立足，译笔必须敏捷如击剑。"
    },
    {
        "id": 4,
        "original_id": 4,
        "work_title_cn": "理想丈夫",
        "translator": "余光中",
        "translation_text": """第三幕：
戈林勋爵：“爱自己，是终身浪漫的开始。”
雪夫利夫人：“所谓道德，不过是我们对待自己私下讨厌的人所采取的态度罢了。”
戈林勋爵：“时尚就是自己穿的衣服；所谓的过时，就是别人穿的衣服。”
戈林勋爵：“女人对事物有惊人的直觉。她们能发现除了一目了然之外的一切事物。”""",
        "translation_school_and_style": "白话与文言融合的雅致现代汉语，余光中将‘To love oneself is the beginning of a lifelong romance’翻译为‘爱自己，是终身浪漫的开始’，节奏如水银泻地。",
        "translator_commentary": "戈林勋爵是王尔德本人的戏剧分身。译者在处理反向警句时，刻意压抑从句缠绕，以警句短刀直击受众耳膜。"
    },
    {
        "id": 5,
        "original_id": 5,
        "work_title_cn": "自深深处",
        "translator": "朱纯深",
        "translation_text": """痛苦是一个漫长而漫长的时刻。我们无法用四季来划分它。我们只能记录它的情绪，并记下它们的周期重现。
哪里有哀伤，哪里就是圣地。总有一天，人们会明白这意味着什么。在此之前，他们对生命将一无所知。
在悲伤的背后，永远是悲伤。退缩的伤口，是渴望痊愈的伤口。
我必须让我身上发生的一切都化为对我有益的事物。木板床、令人作呕的饭食、粗糙的麻绳搓成麻屑直到指尖痛得发木……沉默、孤独、耻辱——所有这一切，我都必须将它们转化为精神的体验。""",
        "translation_school_and_style": "沉郁凄美、如泣如诉的哲理散文风格，句式长短错落，音调哀而不伤，具有极强的心灵净化力量。",
        "translator_commentary": "朱纯深译本被学术界誉为传神典范，把王尔德在深渊中淬炼出的尊严与忏悔精准转化为汉语的崇高美感。"
    },
    {
        "id": 6,
        "original_id": 6,
        "work_title_cn": "谎言的衰落",
        "translator": "萧乾 / 傅惟慈",
        "translation_text": """薇薇安：“生活模仿艺术，远甚于艺术模仿生活。这不仅是因为生活具有模仿的本能，更是因为生活的自觉目标就是寻找自我表达，而艺术正提供了某些优美的形式，使生活得以实现那种活力。”
薇薇安：“说谎，即讲述优美而不真实的事情，才是艺术的真正目的。”
薇薇安：“事物之所以存在，是因为我们看见了它们；而我们看见什么，以及如何看见，取决于影响过我们的艺术。看一样东西与真正看见一样东西，是两码事。”""",
        "translation_school_and_style": "思辨锋利、论辩色彩浓厚的知性散文风范，概念界定清晰，层层剥茧。",
        "translator_commentary": "王尔德在此提出了美学史上最著名的哥白尼式反转——不是艺术抄袭自然，而是大自然与生活因为艺术家的滤镜才获得了形式。"
    },
    {
        "id": 7,
        "original_id": 7,
        "work_title_cn": "社会主义下人的灵魂",
        "translator": "黄源",
        "translation_text": """自私不是按自己希望的方式生活，而是要求别人按照自己希望的方式生活。无私则是让别人的生活顺其自然，不去干预他们。
自私总是企图在它周围创造绝对雷同的人性格局；无私则承认无限的多样性是令人欣喜的事，接受它、默许它、享受它。
一张没有包含乌托邦的世界地图，根本不值得多看一眼，因为它遗漏了人类一直在登陆的那个国度。""",
        "translation_school_and_style": "明晰洗练的政论与伦理随笔文体，将王尔德对极端个人主权的捍卫转化为振聋发聩的思想宣言。",
        "translator_commentary": "彻底划清自由与控制欲的界限。王尔德对‘自私’概念的翻转定义，是整个近代伦理学中最具穿透力的智慧之光。"
    },

    # 莎士比亚
    {
        "id": 8,
        "original_id": 8,
        "work_title_cn": "哈姆雷特",
        "translator": "朱生豪",
        "translation_text": """第三幕 第一场：
生存还是毁灭，这是一个值得考虑的问题；
默然忍受命运暴虐的毒箭，
或是挺身反抗人世的无涯的苦难，
通过斗争把它们扫清，这两种行为，哪一种更高贵？
死了；睡着了；什么都完了；
要是在这一种睡眠之中，我们心头的创痛，
以及其他无数血肉之躯所不能免的打击，都可以从此消失，
那正是我们求之不得的结局。

第二幕 第二场：
人类是一件多么了不起的杰作！多么高贵的理性！多么伟大的力量！多么优美的仪表！多么文雅的举动！在行为上多么像一个天使！在智慧上多么像一个天神！宇宙的精华！万物的灵长！""",
        "translation_school_and_style": "朱生豪译本神韵独绝，文白相融，将莎翁抑扬格五音步诗剧转化为兼具崇高气势与诗意节奏的中文典范。",
        "translator_commentary": "朱生豪在日寇侵略与战乱贫病中以孤勇译就莎剧全集。梁实秋赞其：‘才力宏富，字字精审’，其‘生存还是毁灭’成为整个华语文化最顶级的戏剧母句。"
    },
    {
        "id": 9,
        "original_id": 9,
        "work_title_cn": "罗密欧与朱丽叶",
        "translator": "朱生豪",
        "translation_text": """第二幕 第二场：
朱丽叶：“罗密欧啊，罗密欧！为什么你偏偏是罗密欧？否认你的父亲，抛弃你的姓名吧；如果你不肯，只要指天发誓做我的爱人，我也不再做卡普莱特家族的人。
只有你的名字才是我的仇敌；你即使不姓蒙太古，也依然是那个你。姓名本来是没有意义的；我们叫做玫瑰的这一种花，要是换了个名字，闻起来也依然同样芬芳。”

第二幕 第六场：
劳伦斯神父：“这些狂暴的快乐往往走向狂暴的结局，在它们的极盛时终结，就像火与火药，在相吻的一刹那归于毁灭。”""",
        "translation_school_and_style": "极具青年抒情激情的华彩诗文，‘玫瑰换了个名字依然同样芬芳’精准传递出存在先于标签的深刻本质。",
        "translator_commentary": "朱生豪把青春热恋的盲目狂喜与宿命悲剧的阴影融合在同一种音色中，语言既像蜜糖又像闪电。"
    },
    {
        "id": 10,
        "original_id": 10,
        "work_title_cn": "十四行诗·第18首",
        "translator": "屠岸 / 梁宗岱",
        "translation_text": """我怎么能够把你比作夏天？
你比夏天更可爱、更温婉：
狂风摇撼着五月娇艳的花蕊，
夏天的期限也未免太短……
但你永恒的夏天绝不会凋零，
你所拥有的美也绝不会丧失，
死神也不能夸口你漫游在它的阴影，
当你在不朽的诗行中与时间同长：
只要人类还能呼吸，眼睛还能看见，
这首诗就会活着，赋予你永恒的生命。""",
        "translation_school_and_style": "严格遵循十四行诗格律与顿挫，押韵严整，将莎翁对诗歌抵御时间腐蚀的骄傲信念完美还原。",
        "translator_commentary": "梁宗岱与屠岸译本展现了中国新诗翻译形式美与音律美的最高造诣，‘永恒的夏天绝不会凋零’成为抵抗衰老的无上赞歌。"
    },

    # 杜拉斯
    {
        "id": 11,
        "original_id": 11,
        "work_title_cn": "情人",
        "translator": "王道乾",
        "translation_text": """我已经老了。有一天，在一处公共场所的大厅里，有一个男人向我走来。他主动介绍自己，他对我说：“我认识你，永远记得你。那时候，你还很年轻，人人都说你美，现在，我是特地来告诉你，对我来说，我觉得现在你比年轻的时候更美，那时你是年轻女人，与你年轻时相比，我更爱你现在备受摧残的面容。”

在我的一生中，太快就已经太迟了。十八岁的时候，一切都已经太迟了。在十八岁和二十五岁之间，我的面容偏离了预定的轨道。在十八岁的时候，我变老了。""",
        "translation_school_and_style": "当代中国文学翻译的封神之作。王道乾以凝练纯净、音节舒缓沉静的白话，创造出甚至超越法文原著的汉语音乐感与沧桑韵致。",
        "translator_commentary": "王小波在《我的师承》中顶礼膜拜：“查良铮先生和王道乾先生对我的文学创作有至深的影响……王道乾先生译杜拉斯的《情人》，开篇那几句，字字珠玑，行云流水，这才是真正的现代汉语纯正之美。”"
    },

    # 菲茨杰拉德
    {
        "id": 12,
        "original_id": 12,
        "work_title_cn": "了不起的盖茨比",
        "translator": "巫宁坤",
        "translation_text": """盖茨比信奉这盏绿灯，这个一年年在我们眼前渐渐远去的极乐的未来。它从前逃脱了我们的追求，不过没关系——明天我们跑得更快一点，把胳膊伸得更远一点……总有一天会有一个晴朗的早晨——
于是我们奋力向前划，逆水行舟，不停地倒退，退入过去。

我年纪还轻、阅历不深的时候，我父亲教导过我一句话，我至今还在心头回想。
“每逢你想要批评任何人的时候，”他对我说，“你就记住，这个世界上所有的人，并不是个个都有过你拥有的那些优越条件。”""",
        "translation_school_and_style": "巫宁坤译本被公认为《了不起的盖茨比》中文翻译的不二定本。笔触苍凉洗练，将迷惘一代的虚无与绝望浪漫融于一体。",
        "translator_commentary": "末句‘逆水行舟，不停地倒退，退入过去’（boats against the current, borne back ceaselessly into the past）被称为英语文学最伟大的结尾之一，巫译的节奏与诗意已成为中文文学经典。"
    },

    # 海明威
    {
        "id": 13,
        "original_id": 13,
        "work_title_cn": "老人与海",
        "translator": "海观 / 李继宏",
        "translation_text": """他是个独自在湾流中一条小船上钓鱼的老人，至今已去了八十四天，一条鱼也没逮住。
“一个人并不是生来要给打败的，”他说。“你尽可以把他消灭掉，可就是打不败他。”
“不抱希望是傻透了，”他想，“而且我相信那是罪过。”
“现在不是去想你没有什么的时候。想想利用你现有的东西能做什么吧。”""",
        "translation_school_and_style": "硬汉派极简短句，剔除一切华而不实的修饰，用骨骼和肌肉般的硬朗线条构筑语言。",
        "translator_commentary": "‘人可以被毁灭，但不能被打败’，这十个汉字成为了二十世纪全人类坚韧生命意志的终极象征。"
    },
    {
        "id": 14,
        "original_id": 14,
        "work_title_cn": "流动的盛宴",
        "translator": "汤永宽",
        "translation_text": """假如你有幸年轻时在巴黎生活过，那么此后一生中不论去到哪里，她都会与你同在，因为巴黎是一席流动的盛宴。
巴黎永远没有尽头，每一个在巴黎生活过的人，记忆都与其他人不同。无论我们是谁，无论巴黎如何改变，无论去到那里有多困难或者多容易，我们总会回到那里。""",
        "translation_school_and_style": "温情脉脉与清澈明亮的回忆录语调，‘流动的盛宴’翻译极为传神，‘盛宴’与‘流动’相得益彰。",
        "translator_commentary": "汤永宽将‘moveable feast’译为‘流动的盛宴’，成为了文化界、广告界、生活方式领域被引用频率最高的传世概念之一。"
    },

    # 加缪
    {
        "id": 15,
        "original_id": 15,
        "work_title_cn": "局外人",
        "translator": "柳鸣九 / 郭宏安",
        "translation_text": """今天，妈妈死了。也许是昨天，我不知道。我收到养老院发来的电报：“母死。明日葬。顺致哀忱。”这等于什么也没说。也许就是昨天。
为了让一切都得到圆满，为了让我感到不再那么孤独，我唯一的愿望是：在对我处刑的那一天，有许多看热闹的人来，并且用仇恨的呐喊声向我迎接。""",
        "translation_school_and_style": "零度情感、冰冷直白的实录文风。彻底摒弃道德评判与抒情渲染，以冷峻的诚实撕碎世俗假面。",
        "translator_commentary": "柳鸣九评注：第一句话看似冷血，实则是现代人拒绝被虚伪仪式绑架的最彻底真实。这种短促冷峻的行文方式深刻影响了整个荒诞派文学。"
    },
    {
        "id": 16,
        "original_id": 16,
        "work_title_cn": "西西弗神话",
        "translator": "杜小真",
        "translation_text": """真正严肃的哲学问题只有一个：那就是自杀。判断生命是否值得活下去，就是在回答哲学的根本问题。
向着高处拼搏的本身，就足以充实一个人的心灵。必须想象西西弗是幸福的。""",
        "translation_school_and_style": "哲学思辨的严密与散文诗意的高昂合二为一，‘必须想象西西弗是幸福的’断言如金石之声。",
        "translator_commentary": "杜小真指出加缪在此彻底击碎了传统虚无主义——荒诞不是绝望的借口，而是清醒生活与英雄主义反抗的起点。"
    },

    # 毛姆
    {
        "id": 17,
        "original_id": 17,
        "work_title_cn": "月亮与六便士",
        "translator": "傅惟慈",
        "translation_text": """我想告诉思特里克兰德，这是一次荒唐的冒险，他正在为一个幻影抛弃一份稳固的地位和一个舒适的家。
“我告诉你我必须画画，”他重复道。
“我身不由己。一个人要是掉进水里，他游得好不好并不重要：他必须挣扎着爬出来，否则他就会淹死。”
满地都是六便士，他却抬头看见了月亮。""",
        "translation_school_and_style": "英国式克制嘲讽与内核热烈激情的精妙平衡，傅惟慈译笔流利自然，世故而又深情。",
        "translator_commentary": "‘满地都是六便士，他却抬头看见了月亮’虽为后人概括毛姆书名之深意，但经傅惟慈译介后，已成为华语年轻人追求梦想精神图腾的代名词。"
    },
    {
        "id": 18,
        "original_id": 18,
        "work_title_cn": "刀锋",
        "translator": "周煦良",
        "translation_text": """一把刀的锋刃很难越过；因此智者说，得救之道是困难的。
“我想弄清楚到底有没有上帝。我想弄明白恶为什么存在。我想知道我到底有没有不朽的灵魂，还是当我死后一切就都结束了。”
拉里：“我一直在考虑你说的话。我不想买东西，我也不想赚钱。我想晃荡。”""",
        "translation_school_and_style": "周煦良先生民国文人底蕴的翻译，文字温润通达、恬淡从容，契合拉里在东方哲学中寻得平静的心境。",
        "translator_commentary": "周煦良把拉里的‘loaf’译作‘晃荡’，神来之笔，把一种形而上的哲学漫游与对抗消费主义的松弛感写到了极致。"
    },

    # 茨威格
    {
        "id": 19,
        "original_id": 19,
        "work_title_cn": "人类群星闪耀时",
        "translator": "舒昌善 / 姜乙",
        "translation_text": """这种戏剧性集中、如此充满宿命的时刻——在这样的时刻，一个超越时间的决定被压缩在单一的日期、单一的时辰，往往只是一分钟之内——在个人的生命中是罕见的，在历史的进程中同样罕见。
一个人生命中最大的幸运，莫过于在他的人生中途，即在他年富力强时发现了自己生活的使命。""",
        "translation_school_and_style": "浓郁炽热的德语交响乐般句法，排比重叠，气势恢宏，将历史的偶然而必然演绎得惊心动魄。",
        "translator_commentary": "舒昌善与姜乙译本保留了茨威格文字特有的电击感，‘群星闪耀’的瞬间比漫长平庸世纪更具照亮未来的恒久光辉。"
    },
    {
        "id": 20,
        "original_id": 20,
        "work_title_cn": "一个陌生女人的来信",
        "translator": "张荣昌",
        "translation_text": """致你，从未认识过我的你……
我的孩子昨天死了——三天三夜里我同死神搏斗，争夺这条娇弱幼小的生命……现在在这个世界上我只有你了，只有你，而你对我却一无所知，你正在毫无察觉地寻欢作乐，或者与世间人事逢场作戏；只有你，从未认识过我，而我却始终爱着你。
在这个世界上，再也没有比置身于人群之中却又孤独生活更可怕的了。""",
        "translation_school_and_style": "惊心动魄的心理独白与神经质的炽热，张荣昌把女主人公极度克制又如海啸般的情感爆发刻画得淋漓尽致。",
        "translator_commentary": "单向爱恋的最高艺术丰碑。译文在‘从未认识’与‘始终爱着’的巨大张力中，呈现出人类孤独与痴绝的极限。"
    },

    # 博尔赫斯
    {
        "id": 21,
        "original_id": 21,
        "work_title_cn": "小径分岔的花园",
        "translator": "王永年",
        "translation_text": """《小径分岔的花园》是彭㝡心目中的宇宙的一幅不完整但并不虚假的图像。与牛顿和叔本华不同，您的先祖不相信时间的单一和绝对。他相信时间是一个无限的系列，是一张由发散、汇聚和平行的各个时间交织而成的、不断膨胀而令人头晕目眩的网。
时间永远分岔，通向无数的未来。""",
        "translation_school_and_style": "冷静客观、如百科全书考据般精确的博尔赫斯式迷宫语体，王永年直译西班牙文，严谨而充满哲学玄思。",
        "translator_commentary": "王永年精准捕捉了博尔赫斯将物理学与东方哲学化为叙事迷宫的特质，‘时间永远分岔’成为后现代网络思维的元概念。"
    },
    {
        "id": 22,
        "original_id": 22,
        "work_title_cn": "阿莱夫",
        "translator": "王永年",
        "translation_text": """我看见了阿莱夫，从每一个点上看见了它，在阿莱夫里看见了地球，又在地球上看见了阿莱夫……我看见了一座残破的迷宫（那是伦敦），我看见了无休无止的眼眸逼视着我，仿佛在镜子里审视自己；我看见了地球上所有的镜子，而没有一面镜子能映出我的身影……
我感到无限崇敬、无限怜悯。""",
        "translation_school_and_style": "浩瀚宏大而又极致微缩的超现实并置长排比，如宇宙级全息投影在眼前徐徐展开。",
        "translator_commentary": "王永年完美驾驭了博尔赫斯这篇篇幅虽短却包含宇宙万象的奇文，‘在阿莱夫里看见地球’成就全息认知的文学母本。"
    },

    # 泰戈尔
    {
        "id": 23,
        "original_id": 23,
        "work_title_cn": "飞鸟集",
        "translator": "郑振铎",
        "translation_text": """夏天的飞鸟，飞到我的窗前唱歌，又飞去了。秋天的黄叶，它们没有什么可唱的，只叹息一声，飞落在那里。
生如夏花之绚烂，死如秋叶之静美。
如果你因错过了太阳而流泪，那么你也要错过群星了。
世界在它的爱人面前，卸下了它浩瀚的假面。它变得小如一首歌，小如一个永恒的吻。""",
        "translation_school_and_style": "现代白话诗翻译的永恒冠冕。郑振铎以绝顶的东方诗意重构泰戈尔，‘生如夏花之绚烂，死如秋叶之静美’的汉语美感超越原文。",
        "translator_commentary": "郑振铎译本是双语翻译史上的奇迹，文字清澈如晨露，将宇宙生命的大欢喜与大寂静以东方水墨般的极简呈现。"
    },

    # 卡夫卡
    {
        "id": 24,
        "original_id": 24,
        "work_title_cn": "变形记",
        "translator": "叶廷芳",
        "translation_text": """一天清晨，格里高尔·萨姆沙从不安的睡梦中醒来，发现自己躺在床上变成了一只巨大的甲虫。
他仰卧着，那坚硬得像铁甲一般的背贴着床；他稍稍抬起头，看见了自己的腹部，那上面高高隆起，呈棕褐色，还被许多弓形的硬片分成一段一段……
“我出了什么事啦？”他想。这并不是做梦。""",
        "translation_school_and_style": "叶廷芳先生卡夫卡权威译本。用最一本正经、细致入微的写实白描，去叙述最荒诞不可理喻的事实，形成震撼的反差张力。",
        "translator_commentary": "开篇不作任何解释直接呈现荒诞结果，‘这并不是做梦’撕裂了安全感与日常平庸，成为二十世纪现代主义文学最伟大的开篇之一。"
    }
]


# ── 3. 金句库 (Master Writers Golden Quotes) ──
GOLDEN_QUOTES_DATA: List[Dict[str, Any]] = [
    # ── 王尔德金句群 (Oscar Wilde Epigrams Matrix) ──
    {
        "id": 301,
        "original_id": 4,
        "translation_id": 4,
        "writer_name_cn": "奥斯卡·王尔德",
        "writer_name_en": "Oscar Wilde",
        "source_work": "《理想丈夫 (An Ideal Husband)》",
        "original_quote_lang": "To love oneself is the beginning of a lifelong romance.",
        "translated_quote_cn": "爱自己，是终身浪漫的开始。",
        "translator": "余光中",
        "rhetorical_and_paradox_mechanism": "反向常识与悦己立论：彻底颠覆传统将‘爱他人、奉献牺牲’视为唯一的崇高规训，把‘自恋与自爱’升格为最长情、最忠诚的终身浪漫契约。",
        "theme_tags_json": json.dumps(["悦己与浪漫", "独立女性", "精神主权", "反讨好人格"], ensure_ascii=False),
        "copywriting_application": "当代独立女性、单身经济、轻奢美妆、个人疗愈、悦己生活方式顶级Slogan母体；消灭讨好他人，确立自我精神主权。"
    },
    {
        "id": 302,
        "original_id": 2,
        "translation_id": 2,
        "writer_name_cn": "奥斯卡·王尔德",
        "writer_name_en": "Oscar Wilde",
        "source_work": "《温夫人的扇子 (Lady Windermere's Fan)》",
        "original_quote_lang": "We are all in the gutter, but some of us are looking at the stars.",
        "translated_quote_cn": "我们都在阴沟里，但仍有人仰望星空。",
        "translator": "余光中",
        "rhetorical_and_paradox_mechanism": "极端高低反差并置：将现实的污浊卑微（阴沟）与精神的纯粹无限（星空）暴力并置，以残酷的清醒托起不死的浪漫与崇高。",
        "theme_tags_json": json.dumps(["理想主义", "逆境崛起", "星空精神", "反内卷"], ensure_ascii=False),
        "copywriting_application": "创业精神、逆境前行、大厂打工人反内卷嘴替、硬核科技企业理想主义品牌宣言；认清生活的泥泞后依然选择昂首前行。"
    },
    {
        "id": 303,
        "original_id": 1,
        "translation_id": 1,
        "writer_name_cn": "奥斯卡·王尔德",
        "writer_name_en": "Oscar Wilde",
        "source_work": "《道连·格雷的画像 (The Picture of Dorian Gray)》",
        "original_quote_lang": "I can resist everything except temptation.",
        "translated_quote_cn": "我能抗拒一切，除了诱惑。",
        "translator": "荣如德",
        "rhetorical_and_paradox_mechanism": "全称否定与致命倒戈：前半句伪装成圣人般的克制与定力（抗拒一切），后半句瞬间缴械投降（除了诱惑），幽默中撕碎人性的伪善面具。",
        "theme_tags_json": json.dumps(["欲望与诱惑", "放纵快乐", "幽默自嘲", "美食诱惑"], ensure_ascii=False),
        "copywriting_application": "高端美食、烘焙甜点、深夜放纵饮品、购物狂欢节促销；给消费者的放纵欲望一个完全合理且可爱的借口。"
    },
    {
        "id": 304,
        "original_id": 7,
        "translation_id": 7,
        "writer_name_cn": "奥斯卡·王尔德",
        "writer_name_en": "Oscar Wilde",
        "source_work": "《名言与杂感 (Aphorisms)》",
        "original_quote_lang": "Be yourself; everyone else is already taken.",
        "translated_quote_cn": "做你自己，因为别人已经有人做了。",
        "translator": "公认名译",
        "rhetorical_and_paradox_mechanism": "无懈可击的荒谬正论：用最无可辩驳的客观物理事实（每个人都是唯一占位的物理存在），证明‘模仿他人是彻底的荒唐’，极具心智穿透力。",
        "theme_tags_json": json.dumps(["做自己", "个性潮流", "打破标签", "拒绝平庸"], ensure_ascii=False),
        "copywriting_application": "潮牌服饰、个性化定制、无性别穿搭、打破容貌焦虑；鼓励受众摆脱容貌身材焦虑与社会标准化流水线。"
    },
    {
        "id": 305,
        "original_id": 2,
        "translation_id": 2,
        "writer_name_cn": "奥斯卡·王尔德",
        "writer_name_en": "Oscar Wilde",
        "source_work": "《温夫人的扇子 (Lady Windermere's Fan)》",
        "original_quote_lang": "There are only two tragedies in life: one is not getting what one wants, and the other is getting it.",
        "translated_quote_cn": "生活中只有两种悲剧：一种是没有得到想要的东西，另一种是得到了它。",
        "translator": "余光中",
        "rhetorical_and_paradox_mechanism": "双重否定与叔本华式欲望困境：得不到是匮乏的痛苦，得到了是虚无的厌倦；将欲望的本质以冷酷的对称句式点破。",
        "theme_tags_json": json.dumps(["欲望哲学", "悲剧悖论", "精神追求", "超越物质"], ensure_ascii=False),
        "copywriting_application": "高端艺术品、跑车、收藏级腕表；促使受众超越物质占有，去追求过程中的精神震颤与永恒追寻。"
    },
    {
        "id": 306,
        "original_id": 1,
        "translation_id": 1,
        "writer_name_cn": "奥斯卡·王尔德",
        "writer_name_en": "Oscar Wilde",
        "source_work": "《道连·格雷的画像 (The Picture of Dorian Gray)》",
        "original_quote_lang": "Nowadays people know the price of everything and the value of nothing.",
        "translated_quote_cn": "如今的人知道所有东西的价钱，却对它们的价值一无所知。",
        "translator": "荣如德",
        "rhetorical_and_paradox_mechanism": "概念偷换与深刻讽刺：巧妙剥离‘价格（Price：标签上的数字）’与‘价值（Value：灵魂的重量）’，猛烈抨击拜金世俗的浅薄。",
        "theme_tags_json": json.dumps(["价值与价格", "匠心精神", "文化底蕴", "超越拜金"], ensure_ascii=False),
        "copywriting_application": "匠心手工、文化遗产、艺术电影、独立书店；唤醒公众关注金钱之外无价的陪伴、灵性与时光。"
    },
    {
        "id": 307,
        "original_id": 1,
        "translation_id": 1,
        "writer_name_cn": "奥斯卡·王尔德",
        "writer_name_en": "Oscar Wilde",
        "source_work": "《道连·格雷的画像 (The Picture of Dorian Gray)》",
        "original_quote_lang": "The only way to get rid of a temptation is to yield to it.",
        "translated_quote_cn": "摆脱诱惑的唯一方法，是向它屈服。",
        "translator": "荣如德",
        "rhetorical_and_paradox_mechanism": "以顺为克逆反修辞：表面上看是向欲望投降，实质是击破压抑本能的神经官能症；唯有体验过，心智才能真正解脱放下。",
        "theme_tags_json": json.dumps(["释放欲望", "心理疗愈", "当下体验", "逃离压抑"], ensure_ascii=False),
        "copywriting_application": "旅游度假、周末逃跑企划、舌尖美味释放；让受众放下道德内耗，果断为当下的快乐买单。"
    },
    {
        "id": 308,
        "original_id": 3,
        "translation_id": 3,
        "writer_name_cn": "奥斯卡·王尔德",
        "writer_name_en": "Oscar Wilde",
        "source_work": "《不可儿戏 (The Importance of Being Earnest)》",
        "original_quote_lang": "It is absurd to divide people into good and bad. People are either charming or tedious.",
        "translated_quote_cn": "把人分成好人和坏人是荒谬的。人要么迷人，要么乏味。",
        "translator": "余光中",
        "rhetorical_and_paradox_mechanism": "审美标准取代道德审判：王尔德唯美主义核心纲领——美与有趣是一切价值的度量衡；道德教条往往产生伪善，唯有魅力能直击灵魂。",
        "theme_tags_json": json.dumps(["魅力人设", "审美至上", "有趣灵魂", "拒绝乏味"], ensure_ascii=False),
        "copywriting_application": "高端沙龙香水、社交软件破冰、先锋设计大展；倡导做个生动有趣的人，而非循规蹈矩的平庸好人。"
    },
    {
        "id": 309,
        "original_id": 2,
        "translation_id": 2,
        "writer_name_cn": "奥斯卡·王尔德",
        "writer_name_en": "Oscar Wilde",
        "source_work": "《温夫人的扇子 (Lady Windermere's Fan)》",
        "original_quote_lang": "Experience is simply the name we give our mistakes.",
        "translated_quote_cn": "经验，不过是每个人给自己犯过的错误起的名字。",
        "translator": "余光中",
        "rhetorical_and_paradox_mechanism": "庄严崇高去伪存真：将世人挂在嘴边自傲的‘经验’剥去神圣光环，还其‘失败与踩坑’的狼狈原貌，幽默中带着沧桑释怀。",
        "theme_tags_json": json.dumps(["拥抱失败", "创业试错", "经验真相", "释然自嘲"], ensure_ascii=False),
        "copywriting_application": "职场新人鼓励、创业投资复盘、试错型学习平台；‘不怕犯错，每一个错误都是进化的台阶’。"
    },
    {
        "id": 310,
        "original_id": 7,
        "translation_id": 7,
        "writer_name_cn": "奥斯卡·王尔德",
        "writer_name_en": "Oscar Wilde",
        "source_work": "《社会主义下人的灵魂 (The Soul of Man under Socialism)》",
        "original_quote_lang": "Selfishness is not living as one wishes to live, it is asking others to live as one wishes to live.",
        "translated_quote_cn": "过自己想要的生活不是自私；要求别人过自己想要的生活，才是自私。",
        "translator": "黄源",
        "rhetorical_and_paradox_mechanism": "道德边界重新划定：彻底厘清‘个人边界’与‘控制欲’的区别，把自由主权从道德绑架的泥潭中拯救出来。",
        "theme_tags_json": json.dumps(["个人边界", "拒绝道德绑架", "自由主权", "反精神控制"], ensure_ascii=False),
        "copywriting_application": "反原生家庭精神内耗、年轻人自由职业、独立居住空间设计；击碎传统的道德绑架与职场规训。"
    },

    # ── 其他大师经典金句 (Master Writers Epigrams Matrix) ──
    {
        "id": 311,
        "original_id": 8,
        "translation_id": 8,
        "writer_name_cn": "威廉·莎士比亚",
        "writer_name_en": "William Shakespeare",
        "source_work": "《哈姆雷特 (Hamlet)》",
        "original_quote_lang": "To be, or not to be, that is the question.",
        "translated_quote_cn": "生存还是毁灭，这是一个值得考虑的问题。",
        "translator": "朱生豪",
        "rhetorical_and_paradox_mechanism": "二元生死终极对立：将全人类面临的一切抉择、困顿与觉醒，压缩在‘生存与毁灭’这两个不可调和的极端词汇中。",
        "theme_tags_json": json.dumps(["终极抉择", "存在困境", "战略十字路口", "觉醒"], ensure_ascii=False),
        "copywriting_application": "企业转型战略演讲、重大行业分水岭发布会、个人人生转折点纪录片；面对风浪时的至高发问。"
    },
    {
        "id": 312,
        "original_id": 9,
        "translation_id": 9,
        "writer_name_cn": "威廉·莎士比亚",
        "writer_name_en": "William Shakespeare",
        "source_work": "《罗密欧与朱丽叶 (Romeo and Juliet)》",
        "original_quote_lang": "These violent delights have violent ends.",
        "translated_quote_cn": "这些狂暴的快乐，往往走向狂暴的结局。",
        "translator": "朱生豪",
        "rhetorical_and_paradox_mechanism": "同源词回旋与因果宿命：‘狂暴’（violent）两次敲击，在狂喜的高潮处预告毁灭的深渊，极具悲剧崇高张力。",
        "theme_tags_json": json.dumps(["狂喜与毁灭", "宿命张力", "激情警戒", "美学警示"], ensure_ascii=False),
        "copywriting_application": "金融杠杆警示、极端运动安全提醒、赛博朋克科幻影视宣发；在激情中保持冷峻反思。"
    },
    {
        "id": 313,
        "original_id": 10,
        "translation_id": 10,
        "writer_name_cn": "威廉·莎士比亚",
        "writer_name_en": "William Shakespeare",
        "source_work": "《十四行诗·第18首 (Sonnet 18)》",
        "original_quote_lang": "Shall I compare thee to a summer's day? Thou art more lovely and more temperate.",
        "translated_quote_cn": "我怎么能够把你比作夏天？你比夏天更可爱、更温婉。",
        "translator": "梁宗岱 / 屠岸",
        "rhetorical_and_paradox_mechanism": "反向设问与超越自然：以夏天之热烈起兴，却断然否决将对方比作夏天，因为对方超越了自然的局限与短促。",
        "theme_tags_json": json.dumps(["极度赞美", "温婉之美", "东方浪漫", "超越自然"], ensure_ascii=False),
        "copywriting_application": "高端珠宝腕表告白信、奢华香氛、高定婚纱品牌主张；给心上人最高级、最克制的赞歌。"
    },
    {
        "id": 314,
        "original_id": 11,
        "translation_id": 11,
        "writer_name_cn": "玛格丽特·杜拉斯",
        "writer_name_en": "Marguerite Duras",
        "source_work": "《情人 (L'Amant)》",
        "original_quote_lang": "J'aimais moins votre visage de jeune femme que celui que vous avez maintenant, dévasté.",
        "translated_quote_cn": "与你年轻的时候相比，我更爱你现在备受摧残的面容。",
        "translator": "王道乾",
        "rhetorical_and_paradox_mechanism": "反向审美与岁月神圣化：颠覆全人类对少女胶原蛋白的浅薄趋附，将‘备受摧残的面容’升华为带有灵魂重力与岁月烙印的终极之美。",
        "theme_tags_json": json.dumps(["反容貌焦虑", "岁月深情", "灵魂重力", "顶级神译"], ensure_ascii=False),
        "copywriting_application": "高端抗衰护肤（打破容貌焦虑）、母爱与岁月纪录片、老艺术家致敬、珍贵岁月礼赞。"
    },
    {
        "id": 315,
        "original_id": 12,
        "translation_id": 12,
        "writer_name_cn": "弗·司各特·菲茨杰拉德",
        "writer_name_en": "F. Scott Fitzgerald",
        "source_work": "《了不起的盖茨比 (The Great Gatsby)》",
        "original_quote_lang": "So we beat on, boats against the current, borne back ceaselessly into the past.",
        "translated_quote_cn": "于是我们奋力向前划，逆水行舟，不停地倒退，退入过去。",
        "translator": "巫宁坤",
        "rhetorical_and_paradox_mechanism": "物理方向与时间方向的宿命逆向：拼尽全力向前划，物理动作是进取的，但水流与命运却永恒地将人推回记忆深处，哀而不伤。",
        "theme_tags_json": json.dumps(["逆水行舟", "追忆往昔", "时代宿命", "坚韧前行"], ensure_ascii=False),
        "copywriting_application": "企业年会年度盘点、致敬一代人奋斗历程、高端名酒敬时光、时代风云纪录片结尾。"
    },
    {
        "id": 316,
        "original_id": 13,
        "translation_id": 13,
        "writer_name_cn": "欧内斯特·海明威",
        "writer_name_en": "Ernest Hemingway",
        "source_work": "《老人与海 (The Old Man and the Sea)》",
        "original_quote_lang": "A man can be destroyed but not defeated.",
        "translated_quote_cn": "人可以被毁灭，但不能被打败。",
        "translator": "海观 / 李继宏",
        "rhetorical_and_paradox_mechanism": "肉体消灭与精神不屈的绝对分割：‘毁灭（Destroyed）’属于肉体与物质的外部客观世界，而‘打败（Defeated）’属于心灵内部主观意志；只要心灵不缴械，精神便永远长存。",
        "theme_tags_json": json.dumps(["硬汉精神", "不可战胜", "坚不可摧", "极限挑战"], ensure_ascii=False),
        "copywriting_application": "越野车抗造性能、极地科考探险、重残运动员逆袭纪录片、硬核国产自主研发打破封锁宣传战役。"
    },
    {
        "id": 317,
        "original_id": 14,
        "translation_id": 14,
        "writer_name_cn": "欧内斯特·海明威",
        "writer_name_en": "Ernest Hemingway",
        "source_work": "《流动的盛宴 (A Moveable Feast)》",
        "original_quote_lang": "If you are lucky enough to have lived in Paris as a young man, then wherever you go for the rest of your life, it stays with you, for Paris is a moveable feast.",
        "translated_quote_cn": "如果你足够幸运，年轻时在巴黎居住过，那么此后无论你到哪里，巴黎都会一直跟着你，因为巴黎是一席流动的盛宴。",
        "translator": "汤永宽",
        "rhetorical_and_paradox_mechanism": "空间实体内化为便携式精神资产：把一个固定地理坐标的城市，隐喻为终身随身携带、随时可以开启享用的精神宴席。",
        "theme_tags_json": json.dumps(["流动的盛宴", "青春养分", "城市记忆", "精神财富"], ensure_ascii=False),
        "copywriting_application": "城市品牌形象宣传片、高校毕业季致辞、全球旅行度假卡、艺术留学生归国创业分享。"
    },
    {
        "id": 318,
        "original_id": 15,
        "translation_id": 15,
        "writer_name_cn": "阿尔贝·加缪",
        "writer_name_en": "Albert Camus",
        "source_work": "《局外人 (L'Étranger)》",
        "original_quote_lang": "Aujourd'hui, maman est morte. Ou peut-être hier, je ne sais pas.",
        "translated_quote_cn": "今天，妈妈死了。也许是昨天，我不知道。",
        "translator": "柳鸣九 / 郭宏安",
        "rhetorical_and_paradox_mechanism": "零度情感反煽情惊雷：在全人类预期最悲痛的情境下，用最冷漠、客观、甚至略带不确定的口吻开篇，瞬间击碎读者惯性伪善。",
        "theme_tags_json": json.dumps(["真实不装", "拒绝伪善", "局外人视角", "解构教条"], ensure_ascii=False),
        "copywriting_application": "反说教品牌态度宣传、新锐青年独立文化、拒绝套路真诚对话；‘拒绝表演式的感动，我们只说真话’。"
    },
    {
        "id": 319,
        "original_id": 16,
        "translation_id": 16,
        "writer_name_cn": "阿尔贝·加缪",
        "writer_name_en": "Albert Camus",
        "source_work": "《西西弗神话 (Le Mythe de Sisyphe)》",
        "original_quote_lang": "Il faut imaginer Sisyphe heureux.",
        "translated_quote_cn": "必须想象西西弗是幸福的。",
        "translator": "杜小真",
        "rhetorical_and_paradox_mechanism": "荒谬困境中的主观胜利：面对客观上毫无终点与意义的无限推石劳役，以主观自由意志确认幸福，彻底剥夺诸神降下惩罚的快感。",
        "theme_tags_json": json.dumps(["英雄主义", "直面荒诞", "自主掌控", "反消极躺平"], ensure_ascii=False),
        "copywriting_application": "长跑马拉松精神、科研人员坐十年冷板凳、程序员深夜攻坚；在周而复始的日常中寻找生命的热望与荣耀。"
    },
    {
        "id": 320,
        "original_id": 17,
        "translation_id": 17,
        "writer_name_cn": "威廉·萨默塞特·毛姆",
        "writer_name_en": "W. Somerset Maugham",
        "source_work": "《月亮与六便士 (The Moon and Sixpence)》",
        "original_quote_lang": "He looked at the moon, and then down at the sixpence lying in the gutter.",
        "translated_quote_cn": "满地都是六便士，他却抬头看见了月亮。",
        "translator": "傅惟慈",
        "rhetorical_and_paradox_mechanism": "天体理想与地表铜臭的绝对象征：‘六便士’是世俗金钱与平庸生存，‘月亮’是不可名状的艺术追求与灵魂解放，视角一低一高界定人生段位。",
        "theme_tags_json": json.dumps(["理想主义", "追逐月亮", "超越世俗", "纯粹热爱"], ensure_ascii=False),
        "copywriting_application": "独立创作人基金、人文艺术展览、青年圆梦计划、打破世俗职业规划；‘别为了捡起满地的硬币，错过了头顶的星月’。"
    },
    {
        "id": 321,
        "original_id": 18,
        "translation_id": 18,
        "writer_name_cn": "威廉·萨默塞特·毛姆",
        "writer_name_en": "W. Somerset Maugham",
        "source_work": "《刀锋 (The Razor's Edge)》",
        "original_quote_lang": "The sharp edge of a razor is difficult to pass over; thus the wise say the path to Salvation is hard.",
        "translated_quote_cn": "一把刀的锋刃很难越过；因此智者说，得救之道是困难的。",
        "translator": "周煦良",
        "rhetorical_and_paradox_mechanism": "锋利物象对精神修行的具象隐喻：用极其微薄、割裂肉体的刀锋，比拟人类在欲望与名利诱惑中寻觅精神救赎的险绝之路。",
        "theme_tags_json": json.dumps(["精神救赎", "刀锋前行", "险绝清修", "终极智慧"], ensure_ascii=False),
        "copywriting_application": "哲学通识课程、高端冥想瑜伽中心、长期主义修行、打破消费内卷的心灵指南。"
    },
    {
        "id": 322,
        "original_id": 19,
        "translation_id": 19,
        "writer_name_cn": "斯蒂芬·茨威格",
        "writer_name_en": "Stefan Zweig",
        "source_work": "《人类群星闪耀时 (Sternstunden der Menschheit)》",
        "original_quote_lang": "Ein größeres Glück kann einem Menschen nicht zuteilwerden, als seine Lebensaufgabe in der Mitte des Lebens zu finden.",
        "translated_quote_cn": "一个人生命中最大的幸运，莫过于在他的人生中途，即在他年富力强时发现了自己生活的使命。",
        "translator": "舒昌善 / 姜乙",
        "rhetorical_and_paradox_mechanism": "人生阶段与天职使命的精准交汇：打破少年轻狂与老年迟暮，点出中年知命、知行合一所能激发出的最大历史创造力。",
        "theme_tags_json": json.dumps(["天职使命", "人生幸运", "坚定方向", "群星闪耀"], ensure_ascii=False),
        "copywriting_application": "高管领导力发展项目、中年二次创业转型平台、战略科学家招募、终身学习者社群。"
    },
    {
        "id": 323,
        "original_id": 21,
        "translation_id": 21,
        "writer_name_cn": "豪尔赫·路易斯·博尔赫斯",
        "writer_name_en": "Jorge Luis Borges",
        "source_work": "《小径分岔的花园 (El jardín de senderos que se bifurcan)》",
        "original_quote_lang": "El tiempo se bifurca perpetuamente hacia innumerables futuros.",
        "translated_quote_cn": "时间永远分岔，通向无数的未来。",
        "translator": "王永年",
        "rhetorical_and_paradox_mechanism": "线性时间的几何发散：打破单向不可逆的时间锁链，把每一个当下界定为衍生出无限可能性的量子原点。",
        "theme_tags_json": json.dumps(["时间分岔", "多元宇宙", "无限可能", "未来科技"], ensure_ascii=False),
        "copywriting_application": "AI前沿科技论坛、开放世界游戏宣发、多元职业选择倡议、未来战略实验室品牌片。"
    },
    {
        "id": 324,
        "original_id": 23,
        "translation_id": 23,
        "writer_name_cn": "拉宾德拉纳特·泰戈尔",
        "writer_name_en": "Rabindranath Tagore",
        "source_work": "《飞鸟集 (Stray Birds)》",
        "original_quote_lang": "Let life be beautiful like summer flowers and death like autumn leaves.",
        "translated_quote_cn": "生如夏花之绚烂，死如秋叶之静美。",
        "translator": "郑振铎",
        "rhetorical_and_paradox_mechanism": "两极物象的诗意平衡：生则极尽热烈狂放如盛夏繁花，逝则极尽安详超脱如深秋落叶，全无恐惧，唯有自然律动的崇高。",
        "theme_tags_json": json.dumps(["生如夏花", "神仙翻译", "生命尊严", "自然诗意"], ensure_ascii=False),
        "copywriting_application": "生命保险关怀、高端临终关怀公益、环保生态树葬、全生命周期健康守护品牌主张。"
    },
    {
        "id": 325,
        "original_id": 23,
        "translation_id": 23,
        "writer_name_cn": "拉宾德拉纳特·泰戈尔",
        "writer_name_en": "Rabindranath Tagore",
        "source_work": "《飞鸟集 (Stray Birds)》",
        "original_quote_lang": "If you shed tears when you miss the sun, you also miss the stars.",
        "translated_quote_cn": "如果你因错过了太阳而流泪，那么你也要错过群星了。",
        "translator": "郑振铎",
        "rhetorical_and_paradox_mechanism": "连锁沉没成本警示：为过去的失去悲伤，不仅无法挽回过去，还会夺走当下面对新美好（群星）的敏锐视力。",
        "theme_tags_json": json.dumps(["告别遗憾", "抓住当下", "心理减压", "走出阴霾"], ensure_ascii=False),
        "copywriting_application": "情绪自愈指南、心理咨询热线、反沉没成本投资理财心态教育、‘向前看，前方依然有漫天繁星’。"
    },
    {
        "id": 326,
        "original_id": 24,
        "translation_id": 24,
        "writer_name_cn": "弗朗茨·卡夫卡",
        "writer_name_en": "Franz Kafka",
        "source_work": "《变形记 (Die Verwandlung)》",
        "original_quote_lang": "Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheuren Ungeziefer verwandelt.",
        "translated_quote_cn": "一天清晨，格里高尔·萨姆沙从不安的睡梦中醒来，发现自己躺在床上变成了一只巨大的甲虫。",
        "translator": "叶廷芳",
        "rhetorical_and_paradox_mechanism": "荒谬现实化冷酷白描：将人性的异化作为不容置疑的既成事实猛烈抛向读者，揭穿社会功利关系下亲情与温情的虚伪脆弱。",
        "theme_tags_json": json.dumps(["现代异化", "反工具人", "关怀人性", "打破冰冷职场"], ensure_ascii=False),
        "copywriting_application": "员工关怀倡议、反过度加班企业文化反思、心理健康体检平台、‘我们是活生生的人，不是绩效报表上的数字’。"
    }
]


def init_master_writers_triplet_kb(db_path: Path = None):
    """Create and populate master_writers_originals, master_writers_translations, master_writers_golden_quotes tables."""
    db_file = db_path or (PROJECT_ROOT / "via54_kb.db")
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    # 1. master_writers_originals 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_writers_originals (
            id INTEGER PRIMARY KEY,
            writer_name_en TEXT NOT NULL,
            writer_name_cn TEXT NOT NULL,
            work_title_en TEXT NOT NULL,
            work_title_cn TEXT NOT NULL,
            source_language TEXT NOT NULL,
            genre TEXT NOT NULL,
            original_text_extract TEXT NOT NULL,
            themes_and_philosophy TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    for r in ORIGINALS_DATA:
        cursor.execute("""
            INSERT OR REPLACE INTO master_writers_originals
            (id, writer_name_en, writer_name_cn, work_title_en, work_title_cn, source_language, genre, original_text_extract, themes_and_philosophy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["id"], r["writer_name_en"], r["writer_name_cn"], r["work_title_en"], r["work_title_cn"],
            r["source_language"], r["genre"], r["original_text_extract"], r["themes_and_philosophy"]
        ))

    # 2. master_writers_translations 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_writers_translations (
            id INTEGER PRIMARY KEY,
            original_id INTEGER NOT NULL,
            work_title_cn TEXT NOT NULL,
            translator TEXT NOT NULL,
            translation_text TEXT NOT NULL,
            translation_school_and_style TEXT NOT NULL,
            translator_commentary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (original_id) REFERENCES master_writers_originals(id)
        );
    """)

    for t in TRANSLATIONS_DATA:
        cursor.execute("""
            INSERT OR REPLACE INTO master_writers_translations
            (id, original_id, work_title_cn, translator, translation_text,
             translation_school_and_style, translator_commentary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            t["id"], t["original_id"], t["work_title_cn"], t["translator"],
            t["translation_text"], t["translation_school_and_style"], t["translator_commentary"]
        ))

    # 3. master_writers_golden_quotes 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_writers_golden_quotes (
            id INTEGER PRIMARY KEY,
            original_id INTEGER,
            translation_id INTEGER,
            writer_name_cn TEXT NOT NULL,
            writer_name_en TEXT NOT NULL,
            source_work TEXT NOT NULL,
            original_quote_lang TEXT NOT NULL,
            translated_quote_cn TEXT NOT NULL,
            translator TEXT NOT NULL,
            rhetorical_and_paradox_mechanism TEXT NOT NULL,
            theme_tags_json TEXT NOT NULL,
            copywriting_application TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (original_id) REFERENCES master_writers_originals(id),
            FOREIGN KEY (translation_id) REFERENCES master_writers_translations(id)
        );
    """)

    for g in GOLDEN_QUOTES_DATA:
        cursor.execute("""
            INSERT OR REPLACE INTO master_writers_golden_quotes
            (id, original_id, translation_id, writer_name_cn, writer_name_en,
             source_work, original_quote_lang, translated_quote_cn, translator,
             rhetorical_and_paradox_mechanism, theme_tags_json, copywriting_application)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            g["id"], g["original_id"], g["translation_id"], g["writer_name_cn"], g["writer_name_en"],
            g["source_work"], g["original_quote_lang"], g["translated_quote_cn"], g["translator"],
            g["rhetorical_and_paradox_mechanism"], g["theme_tags_json"], g["copywriting_application"]
        ))

    conn.commit()
    conn.close()

    # Export JSONs
    orig_json = PROJECT_ROOT / "knowledge" / "master_writers_originals.json"
    orig_json.write_text(json.dumps({
        "version": "v1.0.0",
        "description": "Master Writers Originals Knowledge Base (原本库: 原文、章节、哲学体系)",
        "total_works": len(ORIGINALS_DATA),
        "works": ORIGINALS_DATA
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    trans_json = PROJECT_ROOT / "knowledge" / "master_writers_translations.json"
    trans_json.write_text(json.dumps({
        "version": "v1.0.0",
        "description": "Master Writers Translations Knowledge Base (译本库: 名家译文、流派风格、美学评注)",
        "total_translations": len(TRANSLATIONS_DATA),
        "translations": TRANSLATIONS_DATA
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    quotes_json = PROJECT_ROOT / "knowledge" / "master_writers_golden_quotes.json"
    quotes_json.write_text(json.dumps({
        "version": "v1.0.0",
        "description": "Master Writers Canonical Golden Quotes & Paradox Matrix (金句库: 双语对照、修辞反转机制、品牌文案应用)",
        "total_quotes": len(GOLDEN_QUOTES_DATA),
        "quotes": GOLDEN_QUOTES_DATA
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ Successfully initialized Master Writers Triplet Knowledge Base:")
    print(f"   - {len(ORIGINALS_DATA)} Originals in 'master_writers_originals'")
    print(f"   - {len(TRANSLATIONS_DATA)} Translations in 'master_writers_translations'")
    print(f"   - {len(GOLDEN_QUOTES_DATA)} Golden Epigrams in 'master_writers_golden_quotes'")


if __name__ == "__main__":
    init_master_writers_triplet_kb()
