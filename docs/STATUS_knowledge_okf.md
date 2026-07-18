# via54ADIdeahub Knowledge + OKF 集成 — 状态报告

> 生成时间: 2026-07-14
> 分支: main (before commit)

## 什么是建成

### 1. via54_okf 包 — OKF v0.1 文档处理

- `document.py` — Google OKF v0.1 规范的解析器/序列化器/验证器；符合 §9 一致性（每个非保留 .md 文件都有 YAML frontmatter 和 type 字段）；`_convert_datetime` 确保 `datetime.datetime` 对象被恢复为 ISO 8601 字符串
- `bundle.py` — 递归 bundle 扫描器；概念 ID 解析；`extract_links`（bundle 相对路径、相对路径、外部链接 3 种类型）；符合 §5/§6/§7 路径和 index.md/log.md 保留名称规则
- `cli.py` — `python -m via54_okf validate <dir>` 用于 bundle 一致性检查；50/50 个概念 OK 已验证
- 13 个单元测试全部通过

### 2. via54_store 包 — SQLite + 向量数据模型

- `schema.sql` — 9 张表：bundles、concepts（含 OKF frontmatter 字段）、concept_chunks、chunk_terms（TF-IDF 倒排索引）、chunk_vector_blob、chunk_vector_meta、concept_links、concept_index_aggr、ingest_log
- `store.py` — KBStore CRUD 封装：upsert_bundle、upsert_concept、add_chunk（自动填充 chunk_terms）、add_chunk_vector（float32 BLOB + L2 归一化元数据）、replace_concept_atomic（原子事务）、批量提交
- `embedding.py` — 纯 stdlib 哈希嵌入（blake2b → 2×桶位置 → 带符号贡献 → L2 归一化 → dim=256）
- `retrieval.py` — HybridRetriever：稠密哈希余弦 + 稀疏 TF-IDF 余弦融合（默认权重 0.6 v / 0.4 t）
- `cli.py` — init / stats / search / vectors-stats 子命令
- 13 个单元测试全部通过

### 3. 工具

- `tools/ingest_knowledge.py` — 扫描 ~/Desktop/Knowledge/Idea/By_Industry，推断行业/品牌/case；将所有 .md 类型映射为 OKF 概念（Case Study、Case Overview、Video Catalog、Creative Mix、Folder README、Visual References、Video List）；按段落分块（300 字符，50 重叠）；哈希嵌入（256 维）；写入 via54_kb.db（单次事务每 1000 条提交）；打印 stats + ingest_log
- `tools/export_okf.py` — 导出 SQL → OKF bundle 目录（bundle.yaml、index.md、log.md、case_studies/、videos/、creatives/、folder_readmes/、visual_references/、references/）
- `tools/vector_stats.py` — 覆盖率 / 维度 / 平均 L2 范数 / 零向量 / 各模型统计

## 三方位验证

| 来源 | 证据 |
|---|---|
| **文件系统** | `via54_kb.db` = 231 MB（9 张表已填充）<br>`via54_okf/` — 5 个 .py 文件，9,426+ 行<br>`via54_store/` — 6 个 .py 文件，18,200+ 行<br>`tools/` — 3 个 .py 文件<br>`tests/` — 2 个 .py 文件，26 项测试 |
| **运行时** | 52/52 OKF 导出概念已验证，type 字段一致<br>3/3 roundtrip 已通过<br>52811/52811 个向量覆盖率 100%<br>平均 L2 范数 = 1.0000（完美归一化）<br>0 个零向量<br>1065 秒内完成 1970 个案例 |
| **检索** | 查询 "Apple iPhone advertisement" → #1 为 "Apple iPhone 14 — Relax, It's iPhone – Action Mode"（正确命中）<br>查询 "Cannes Grand Prix" → top 分数 0.85，结果包含 Cannes Lions 关键词 |

## 已知限制

1. **嵌入**：使用 blake2b 哈希技巧（2017 年左右的方法论），而非真正的 transformer 模型（无 numpy/sentence-transformers/torch）。TF-IDF 稀疏路径可在一定程度上弥补——对于关键词层面的概念检索足够好用，但无法感知短语级语义
2. **无 concept_links 填充**：导入器跳过链接提取；导出器仍按概念输出
3. **concept_index_aggr 为空**：无触发器——不会影响读取；汇总信息可直接通过 COUNT 查询实时重建
4. **chunk_terms 使用本地在 chunk_terms 中的 TF**：未进行全局 IDF 存储（检索器在搜索时根据实时 doc_count 计算 IDF），对于即席查询更准确，但在导出时 weight 会变化
5. **文件名清洗**：包含空格和中文字符的原始文件名在 OKF bundle 中保留，便于人类阅读，但 agent 解析可能需要 URL 编码

## 后续 5 步

1. **全量 OKF 导出**：对全部 9881 个概念运行 `export_okf.py`（无 `--limit`），获取完整的 Google 兼容 OKF bundle
2. **concept_links 填充**：向导入器添加 `extract_links()` 支持，将 markdown 链接提取为带类型的边
3. **查询加速**：为 `search` CLI 添加向量缓存预热，使首次查询在 DB 预热后不再分块加载所有 52811 个向量
4. **Web API**：添加 `via54_store serve` 子命令，在 18765 端口运行 HTTP 搜索端点（与现有 `via54_rag_search.py` 兼容）
5. **知识图谱可视化器**：使用 D3Force 或 Google OKF 的 `viz.html` 参考实现，渲染 OKF bundle 的交互式图形视图
