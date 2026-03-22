-- MEGAMIND SCHEMA
-- Designed for expansion: new data sources add source values, not new tables.
-- All intelligence flows through OBSERVATION → synthesis → QUADRANT_STATE / PATTERN.

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ─────────────────────────────────────────────
-- CORE: Every data point that enters the system
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS observation (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  DATETIME NOT NULL DEFAULT (datetime('now')),
    occurred_at DATETIME,                    -- when the event actually happened

    -- Source: which MCP or input produced this
    -- Current: chat | email | calendar | filesystem | web | health |
    --          exercise | sleep | financial | location | reading | social
    -- Future:  any new MCP just adds a new value here
    source      TEXT NOT NULL,

    -- Quadrant relevance (can be NULL if unclear)
    -- spiritual | social | intellectual | physical | startup | meta
    quadrant    TEXT,

    -- Raw content — what actually happened
    content     TEXT NOT NULL,

    -- Structured metadata (JSON) — source-specific fields
    -- e.g. for 'exercise': {"type": "bjj", "duration_min": 90}
    -- e.g. for 'social':   {"person": "John", "medium": "call", "duration_min": 12}
    -- e.g. for 'financial':{"account": "checking", "delta": 500, "net_worth": 142000}
    meta        TEXT,

    -- mem0 memory ID if stored there
    mem0_id     TEXT,

    -- Processing state
    processed   INTEGER NOT NULL DEFAULT 0,  -- 0=raw, 1=synthesized
    importance  REAL DEFAULT 0.5             -- 0-1, updated during synthesis
);

CREATE INDEX IF NOT EXISTS idx_observation_source     ON observation(source);
CREATE INDEX IF NOT EXISTS idx_observation_quadrant   ON observation(quadrant);
CREATE INDEX IF NOT EXISTS idx_observation_occurred   ON observation(occurred_at);
CREATE INDEX IF NOT EXISTS idx_observation_processed  ON observation(processed);


-- ─────────────────────────────────────────────
-- SYNTHESIZED STATE: What Claude reasons over
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS quadrant_state (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    updated_at  DATETIME NOT NULL DEFAULT (datetime('now')),
    quadrant    TEXT NOT NULL,               -- spiritual | social | intellectual | physical | startup
    period      TEXT NOT NULL,               -- daily | weekly | monthly | yearly
    score       REAL,                        -- 0-1 progress toward yearly target
    trend       TEXT,                        -- improving | declining | steady
    insight     TEXT,                        -- Claude's plain-language synthesis
    raw_stats   TEXT                         -- JSON: source-specific metrics
);

CREATE INDEX IF NOT EXISTS idx_qstate_quadrant ON quadrant_state(quadrant, period);


-- ─────────────────────────────────────────────
-- PATTERNS: Behavioral signatures over time
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS pattern (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at      DATETIME NOT NULL DEFAULT (datetime('now')),
    description     TEXT NOT NULL,           -- plain language: "you make impulsive decisions on low-sleep days"
    pattern_type    TEXT,                    -- behavioral | energy | decision | relational | financial | ...
    quadrant        TEXT,
    evidence_count  INTEGER DEFAULT 1,
    confidence      REAL DEFAULT 0.3,        -- grows as evidence accumulates
    first_observed  DATETIME,
    last_observed   DATETIME,
    active          INTEGER DEFAULT 1        -- 0 if pattern seems to have broken
);


-- ─────────────────────────────────────────────
-- PEOPLE: Relationship tracking
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS person (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL,
    relationship        TEXT,                -- friend | family | professional | contact
    last_contact        DATETIME,
    contact_target      TEXT,                -- "weekly" | "monthly" | "7/week" etc
    thread              TEXT,                -- what's ongoing with this person
    notes               TEXT,
    importance          REAL DEFAULT 0.5,    -- 0-1
    meta                TEXT                 -- JSON: additional fields
);

CREATE INDEX IF NOT EXISTS idx_person_last_contact ON person(last_contact);


-- ─────────────────────────────────────────────
-- GOALS: The scoring function
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS goal (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    quadrant    TEXT NOT NULL,
    description TEXT NOT NULL,
    target      TEXT,                        -- measurable target
    current     TEXT,                        -- current state
    deadline    DATE,
    status      TEXT DEFAULT 'active',       -- active | completed | dropped
    sub_goals   TEXT,                        -- JSON array
    notes       TEXT
);


-- ─────────────────────────────────────────────
-- STARTUP: Deal and relationship pipeline
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS startup_entity (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at      DATETIME NOT NULL DEFAULT (datetime('now')),
    entity_type     TEXT NOT NULL,           -- company | contact | deal | investor | ...
    name            TEXT NOT NULL,
    stage           TEXT,                    -- pipeline stage
    last_interaction DATETIME,
    notes           TEXT,
    meta            TEXT                     -- JSON: entity-specific fields
);


-- ─────────────────────────────────────────────
-- SESSIONS: Morning brief log
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS session (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at  DATETIME NOT NULL DEFAULT (datetime('now')),
    ended_at    DATETIME,
    brief       TEXT,                        -- morning brief text
    next_action TEXT,                        -- the one action surfaced
    quadrant_focus TEXT,                     -- which quadrant was prioritized
    notes       TEXT                         -- end-of-session synthesis
);
