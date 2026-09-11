# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2026-09-11

### Added
- **4-Dimensional Similarity Benchmarks (四维相似性对标体系)**:
  - Attached mandatory 4-D similarity benchmarks (🔊读音相似性 / 💡意义相似性 / ✍️表达相似性 / 🏛️结构相似性) to every delivered copy suggestion across all reasoning agents.
  - Guarantees $\ge 3$ distinct creative options with deep 3-D reasoning (Sound + Meaning + Intuition) even without explicit user prompts.
- **Brand Tone Profile Management (`BrandProfileManager`)**:
  - Structured brand persona configs (`apple`, `chagee`, `proya`, `wenjian`) enforcing cadence preference, core spirit, forbidden buzzwords, and micro-sensory anchors.
  - New MCP tool: `manage_brand_profiles` (12 production tools total).
- **Automated 3-D Reverse Ingestion Pipeline (`scripts/scheduled_collect.py`)**:
  - Integrated `MasterLinguisticEngine` to dynamically analyze phonetic cadence, semantic tension, and intuitive neurological triggers on newly crawled industry cases.
- **MCP End-to-End Health Check (`scripts/mcp_health_check.py`)**:
  - Automated 13/13 MCP tool verification suite.
- **Test Suite Expansion**:
  - Added `tests/test_similarity_benchmarks.py` — 27/27 unit tests passing across all engines.

## [2.2.0] - 2026-09-11

### Added
- **Masterclass 3-D Linguistic Laws & Alchemy Engine (`MasterLinguisticEngine`)**:
  - `PhoneticCadenceAnalyzer`: Acoustic symmetry, pitch contour, plosives, resonant open vowels, and 4 Bilingual Harmonization laws.
  - `SemanticTensionDeconstructor`: A!=B cognitive subversion, spacetime contrast, and emotional-functional isomorphism.
  - `IntuitiveSensoryMapper`: 0.5s neurological mirror-neuron trigger actions and concrete imagery mapping.
  - New corpus: `knowledge/masterclass_copywriting_corpus.json` & `knowledge/linguistic_laws_and_cadence.json`.
  - New MCP tool: `analyze_linguistic_laws` (9 production tools total).
- **Test Suite**: 22/22 automated unit tests passing across all engines.

## [2.1.0] - 2026-09-11
- Exemplar reverse-engineering and 5 evolved alternatives.

## [2.0.0] - 2026-09-11
- 7 Subculture guides, 5 slogan archetypes, Copy Polisher, Pun Engine, Critic scoring.
