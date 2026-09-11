<div align="center">

# 🌌 via54ADIdeahub — 智能广告创意全案与大师级语言炼金引擎

> **🌐 Language**: [🇨🇳 中文](#) (current) | [🇺🇸 English](./README_EN.md)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Standard](https://img.shields.io/badge/MCP-1.0.0-green.svg)](https://modelcontextprotocol.io/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![Tests: 22/22 Passing](https://img.shields.io/badge/tests-22%2F22%20passed-brightgreen.svg)](tests/)
[![Architecture: Hybrid RAG](https://img.shields.io/badge/RAG-Hybrid%20%2B%20Critic-orange.svg)](DESIGN.md)

</div>

---

> **专为品牌策划与广告创意人打造的工业级 AI 创意中台。**  
> 深度逆向全网经典文案与大品牌口号，提炼 **【读音声韵 + 意义张力 + 0.5秒神经直觉】** 三大底层公理，融合 **7 大垂直圈层真实语境库**、**中英文混合咬合算法**、**文案深度体检与脱水重构 (Copy Polisher)**、**概念双关推演引擎 (Pun Engine)** 与 **Critic 独立质检评分机制**，通过 **MCP (Model Context Protocol)** 协议赋能 AI 编程与创意工作流。

---

## 🚀 核心能力矩阵

```mermaid
graph TD
    A[用户输入: 创意命题 / 示例文案 / 文案初稿 / 中英混搭] --> B[意图与圈层解析路由]
    
    subgraph 知识库与语境体系
        C1[7大圈层真实语境库<br/>Gay/00后/女性/患者/银发/养宠/户外]
        C2[100+经典与中英混合解构语料库<br/>Apple/Nike/珀莱雅/杜蕾斯/胜加/诚品]
        C3[声律平仄与广告法合规公理库<br/>4大中英咬合律/极限词拦截]
    end
    
    B --> C1
    B --> C2
    B --> C3
    
    subgraph 大师级语言炼金引擎 (MasterLinguisticEngine)
        D0[读音维度: 平仄抑扬/爆破音/开口音/中英对称]
        D1[意义维度: A!=B 观念颠覆/昼夜撕扯/同构隐喻]
        D2[直觉维度: 0.5秒镜像神经元微物象/无损直通大脑]
        D3[5大超越级巅峰文案演化合成]
    end
    
    C1 --> D0
    C2 --> D1
    C3 --> D2
    
    D0 --> D3
    D1 --> D3
    D2 --> D3
    
    subgraph 辅助工具与质检层
        E1[文案体检诊断与脱水重构 Copy Polisher]
        E2[概念双关与谐音推演引擎 Pun Engine]
        E3[独立 Critic 质检打分与合规过滤]
    end
    
    D3 --> E1
    D3 --> E2
    D3 --> E3
    
    E3 --> F[结构化全案输出 / 飞书卡片渲染 / MCP 响应]
```

### 1. 经典文案三维底层公理逆推 (`MasterLinguisticEngine`)
- **🎵 读音维度 (Phonetic Cadence & Acoustic Resonance)**：
  - 律动模型（`4+4` 律绝格、`6+6` 平衡格、`7+7` 对仗格、`3+5` 先声夺人格）。
  - 爆破音密度（`p/b/t/d/k/g` 提供神经击穿感）与开合口尾音共鸣（`a/ang/eng/ong` 余音袅袅）。
  - **中英文混合 4 大咬合律**：轻重音对齐、英文字节与中文等时对称、避免生硬中英夹杂。
- **💡 意义维度 (Semantic Tension & Conceptual Subversion)**：
  - `A != B, C is true`（反常识认知断言，如“性别不是边界线，偏见才是”）。
  - 昼夜/空间/身份的极致撕扯（“白天体面演戏，夜晚肉身除锈”）。
  - 物理动作 $\rightarrow$ 心理情绪的双向同构隐喻（除锈/缓冲/通关/打卡/护甲）。
- **👁️ 人类直觉维度 (Human Neurological Intuition)**：
  - 激活镜像神经元的微动作（呼吸、吞咽、快门、撕开、电梯关门、甩开领带）。
  - 0.5 秒无损直通潜意识，彻底杜绝无画面的假大空形容词。

### 2. 7 大垂直圈层语境知识库 (`audience_language/`)
- **`gay` (LGBT+ 圈层)**：通关、全场、PLAY、开挂、营业、去说教、亲密安全
- **`genz` (00后 / 打工人)**：去班味、精神离职、反内卷、工位除锈、嘴替发疯
- **`women` (独立女性)**：自洽、主场力量、身体疆域、不被定义、松弛感
- **`patient` (医疗健康与患者心声)**：驱散病耻感、大白话痛点、生活掌控权、具象场景
- **`silver` (银发经济与新老年)**：第二人生、不添麻烦、尊严活力、平视陪伴
- **`pet` (养宠一族 / 毛孩子家长)**：毛孩子、情绪解药、治愈、科学喂养、无声告白
- **`outdoor` (山系青年 / 旷野自救)**：去旷野、身体在场、轻装自救、精神庇护所

### 3. 用户初稿诊断与润色工具 (Copy Polisher)
- **全方位体检**：量化健康分（1-5分），自动诊断爹味说教、假大空行话、水词修饰及广告法违规。
- **三维重构方案**：一键输出 **锐利脱水版**、**情绪共鸣版**、**圈层地道版**。

### 4. 概念双关与谐音推演引擎 (Pun Engine)
- 基于表面动作与品牌心智双向推演，评估牵强感与翻车风险（Cringe Risk），杜绝低俗谐音烂梗。

---

## 🛠️ MCP (Model Context Protocol) 9 大工具矩阵

| 工具名称 | 功能描述 |
|:---|:---|
| **`analyze_linguistic_laws`** | 深度分析任意文案（纯中/纯英/中英混搭）的声律平仄、意义张力与直觉物象 |
| **`deconstruct_and_evolve_copy`** | 示例文案 3 维底层逆向解构，推演 5 大声律升维文案 |
| **`reason_creative_strategy`** | 生成 5 大差异化口号全案、品牌宣言、超级符号及 Critic 质检打分 |
| **`polish_and_diagnose_copy`** | 对用户已有文案初稿进行爹味与水词诊断，并输出 3 维重构方案 |
| **`explore_creative_puns`** | 发散概念双关与谐音文案，并提供牵强感与翻车风险质检 |
| **`audit_advertising_compliance`** | 检查文案是否触犯广告法极限词或圈层敏感红线 |
| **`search_audience_language`** | 检索特定圈层的语言特征、黑话指南与禁忌避坑规则 |
| **`search_knowledge_base`** | 跨全行业创意案例与报告进行 TF-IDF 混合检索 |
| **`list_advertising_cases`** | 按行业、品牌、奖项等级（Cannes/Clio/Effie等）筛选案例 |

---

## 📦 快速开始

```bash
git clone https://github.com/veawho/via54ADIdeahub.git
cd via54ADIdeahub

# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 运行全量单元测试
PYTHONPATH=. python3 -m unittest discover -s tests
```

---

## 📄 License
本项目采用 [AGPL-3.0 License](LICENSE) 开源协议。
