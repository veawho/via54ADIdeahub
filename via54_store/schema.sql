-- via54_store schema — unified SQLite data model
-- Bundles + Concepts (OKF specs + .md case reports) + chunks + vectors + TF-IDF

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ── 1. Bundles — top-level metadata for an OKF bundle or knowledge source ──
CREATE TABLE IF NOT EXISTS bundles (
    bundle_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL UNIQUE,
    root_path    TEXT NOT NULL,
    version      TEXT,
    description  TEXT,
    created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    doc_count    INTEGER NOT NULL DEFAULT 0
);

-- ── 2. Concepts — one row per OKF concept node OR per .md case report ──
CREATE TABLE IF NOT EXISTS concepts (
    concept_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    bundle_id     INTEGER NOT NULL,
    rel_path      TEXT NOT NULL,
    type          TEXT NOT NULL,            -- 'concept', 'case', 'document', etc.
    title         TEXT,
    description   TEXT,
    resource      TEXT,                    -- URL / source identifier
    tags_json     TEXT,                    -- JSON array of tags
    timestamp     TEXT,                    -- ISO timestamp for ordering
    source_path   TEXT NOT NULL,           -- absolute file path
    mtime         REAL,                    -- file mtime
    body_size     INTEGER NOT NULL DEFAULT 0,
    body_hash     TEXT,                    -- sha256 hex of body (for idempotency)
    FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE,
    UNIQUE (bundle_id, rel_path)
);

-- ── 3. Concept links — `[text](target)` parsed from concept body ──
CREATE TABLE IF NOT EXISTS concept_links (
    link_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    src_concept_id   INTEGER NOT NULL,
    target_path      TEXT NOT NULL,
    link_kind        TEXT NOT NULL,        -- 'markdown', 'okf-ref', 'url'
    link_text        TEXT,
    position         INTEGER NOT NULL,
    FOREIGN KEY (src_concept_id) REFERENCES concepts(concept_id) ON DELETE CASCADE
);

-- ── 4. Concept chunks — body segmented into chunks ──
CREATE TABLE IF NOT EXISTS concept_chunks (
    chunk_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    concept_id  INTEGER NOT NULL,
    chunk_idx   INTEGER NOT NULL,
    text        TEXT NOT NULL,
    char_start  INTEGER NOT NULL,
    char_end    INTEGER NOT NULL,
    tokens_json TEXT,                    -- JSON array of tokens
    FOREIGN KEY (concept_id) REFERENCES concepts(concept_id) ON DELETE CASCADE,
    UNIQUE (concept_id, chunk_idx)
);

-- ── 5. Chunk terms — inverted index (TF for chunk-term) ──
CREATE TABLE IF NOT EXISTS chunk_terms (
    term      TEXT NOT NULL,
    chunk_id  INTEGER NOT NULL,
    tf        REAL NOT NULL,
    FOREIGN KEY (chunk_id) REFERENCES concept_chunks(chunk_id) ON DELETE CASCADE,
    PRIMARY KEY (term, chunk_id)
);

-- ── 6. Chunk vector meta — dim/norm/model per chunk vector ──
CREATE TABLE IF NOT EXISTS chunk_vector_meta (
    chunk_id  INTEGER PRIMARY KEY,
    dim       INTEGER NOT NULL,
    norm      REAL NOT NULL,
    model     TEXT NOT NULL,
    FOREIGN KEY (chunk_id) REFERENCES concept_chunks(chunk_id) ON DELETE CASCADE
);

-- ── 7. Chunk vector BLOB — actual float32 vector packed ──
CREATE TABLE IF NOT EXISTS chunk_vector_blob (
    chunk_id  INTEGER PRIMARY KEY,
    vec       BLOB NOT NULL,
    model     TEXT NOT NULL,
    FOREIGN KEY (chunk_id) REFERENCES concept_chunks(chunk_id) ON DELETE CASCADE
);

-- ── 8. Concept index aggregate — dashboard accelerator ──
CREATE TABLE IF NOT EXISTS concept_index_aggr (
    concept_id      INTEGER PRIMARY KEY,
    link_count      INTEGER NOT NULL DEFAULT 0,
    chunk_count     INTEGER NOT NULL DEFAULT 0,
    has_vector      INTEGER NOT NULL DEFAULT 0,
    term_count      INTEGER NOT NULL DEFAULT 0,
    last_indexed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── 9. Ingest log — audit trail ──
CREATE TABLE IF NOT EXISTS ingest_log (
    ingest_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at     TEXT,
    kind         TEXT NOT NULL,           -- 'bundle', 'concept', 'case'
    source_path  TEXT,
    inserted     INTEGER NOT NULL DEFAULT 0,
    updated      INTEGER NOT NULL DEFAULT 0,
    skipped      INTEGER NOT NULL DEFAULT 0,
    errors       INTEGER NOT NULL DEFAULT 0,
    notes        TEXT
);

-- ── 10. Creative Cases — Digitaling & TOPYS enriched cases ──
CREATE TABLE IF NOT EXISTS creative_cases (
    case_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    source              TEXT NOT NULL,          -- 'digitaling' | 'topys' | 'other'
    source_url          TEXT UNIQUE NOT NULL,
    title               TEXT NOT NULL,
    brand               TEXT NOT NULL,
    industry            TEXT NOT NULL,
    published_year      INTEGER NOT NULL,       -- 2024, 2025, 2026
    published_date      TEXT,
    agency              TEXT,
    
    -- 创意原点
    brand_context       TEXT,
    product_feature     TEXT,
    market_competition  TEXT,
    consumer_trend      TEXT,
    consumer_insight    TEXT,
    
    -- 核心洞察与目标
    creative_target     TEXT,
    viral_effect        TEXT,
    memory_anchor       TEXT,
    
    -- 社交梗力与口号
    social_meme_tags    TEXT,                   -- JSON array of meme keywords
    campaign_slogan     TEXT,
    brand_slogan        TEXT,
    raw_content         TEXT,
    full_markdown       TEXT,
    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── 11. Pun & Double Entendre Cases ──
CREATE TABLE IF NOT EXISTS pun_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    industry TEXT,
    pun_text TEXT NOT NULL,
    surface_meaning TEXT,
    hidden_meaning TEXT,
    phonetic_pair TEXT,
    audience_type TEXT DEFAULT "default",
    quality_score REAL DEFAULT 4.0,
    critique_notes TEXT,
    example_link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Indexes ──
CREATE INDEX IF NOT EXISTS idx_concepts_type     ON concepts(type);
CREATE INDEX IF NOT EXISTS idx_concepts_bundle   ON concepts(bundle_id);
CREATE INDEX IF NOT EXISTS idx_concepts_resource ON concepts(resource);
CREATE INDEX IF NOT EXISTS idx_chunks_concept    ON concept_chunks(concept_id);
CREATE INDEX IF NOT EXISTS idx_terms_term        ON chunk_terms(term);
CREATE INDEX IF NOT EXISTS idx_links_src         ON concept_links(src_concept_id);
CREATE INDEX IF NOT EXISTS idx_links_target      ON concept_links(target_path);
CREATE INDEX IF NOT EXISTS idx_creative_cases_source ON creative_cases(source);
CREATE INDEX IF NOT EXISTS idx_creative_cases_year   ON creative_cases(published_year);
CREATE INDEX IF NOT EXISTS idx_creative_cases_ind    ON creative_cases(industry);
CREATE INDEX IF NOT EXISTS idx_creative_cases_brand  ON creative_cases(brand);
CREATE INDEX IF NOT EXISTS idx_pun_cases_audience    ON pun_cases(audience_type);
CREATE INDEX IF NOT EXISTS idx_pun_cases_score       ON pun_cases(quality_score);


