# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-09-11

### Added
- **7 Vertical Subculture Context Knowledge Base**: Added comprehensive dialect, lived-moment guidelines, and taboo boundaries for `gay` (LGBT+), `genz` (Anti-burnout / Z-Era), `women` (Female Self-acceptance), `patient` (Healthcare & Patient plain-talk), `silver` (Silver economy / Active retirement), `pet` (Pet parents), and `outdoor` (Mountain youth).
- **5 Slogan Archetypes & Critic Engine**: Integrated Subversive Humor, Unfiltered Voice, Cinematic Narrative, Hardcore Authority, and Subculture Identity in `agents/creative_reasoner.py`, with independent Critic scoring (`emotion_score`, `humanity_score`, `audience_fit_score`).
- **Copy Polisher & Diagnostics Tool**: Built `agents/copy_polisher.py` for automated preachiness / corporate buzzword / water word detection, health scoring, and 3-dimensional rewrites.
- **Double Entendre & Pun Engine**: Built `agents/pun_engine.py` and `pun_cases` SQLite table for conceptual dual-meaning deduction and cringe risk scoring.
- **Compliance & Ad Law Linter**: Created `knowledge/compliance_rules.json` to filter advertising law absolute superlatives and subculture red lines.
- **MCP Server Expansion**: Exposed 7 production MCP tools (`reason_creative_strategy`, `polish_and_diagnose_copy`, `explore_creative_puns`, `audit_advertising_compliance`, `search_audience_language`, `search_knowledge_base`, `list_advertising_cases`).
- **Automated Tests**: Added `tests/test_creative_reasoner.py`, `tests/test_phase2.py`, and `tests/test_mcp_tools.py` (14/14 tests passing).

## [1.1.0] - 2026-06-29

- Add integrations/ for qdrant (25K), chroma (18K), ScrapeGraphAI (27K). Plan RAG migration.

## [1.0.0] - 2026-06-29

### Added
- Initial release with Cannes/Clio advertising cases and TF-IDF search engine.
- GitHub compliance files (LICENSE AGPL-3.0, README, CODEOWNERS, CONTRIBUTING).
