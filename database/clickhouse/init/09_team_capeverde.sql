-- Per-team database for capeverde. Same table shapes as squad_data_store,
-- minus the team_code column (redundant once the DB itself is team-scoped)
-- and minus partitioning (each DB is already a single team's worth of data).
-- Populated by ingestion/partition.py fanning out from squad_data_store.
--
-- Cape Verde is the 8th team, added after the original 7 - their first-ever
-- World Cup qualification (2026) is a real, well-documented underdog story,
-- so they get the same full real-data treatment (Wikipedia squad + TheSportsDB
-- + curated trophies), not synthetic placeholder content.

CREATE DATABASE IF NOT EXISTS capeverde;

CREATE TABLE IF NOT EXISTS capeverde.players (
    player_id UInt32,
    name String,
    position String,
    club String,
    age UInt8,
    overall_rating UInt8,
    nationality String,
    photo_url String,
    team_code String,
    source String        -- data provenance, e.g. 'real:wikipedia' or 'synthetic'
) ENGINE = MergeTree()
ORDER BY player_id;

CREATE TABLE IF NOT EXISTS capeverde.public_stats (
    player_id UInt32,
    goals UInt16,
    assists UInt16,
    key_passes UInt16,
    tackles UInt16,
    rating_avg Float32,
    matches_played UInt16
) ENGINE = MergeTree()
ORDER BY player_id;

CREATE TABLE IF NOT EXISTS capeverde.injuries (
    player_id UInt32,
    injury_type String,
    status String,
    expected_return Date,
    severity String
) ENGINE = MergeTree()
ORDER BY player_id;

CREATE TABLE IF NOT EXISTS capeverde.salaries (
    player_id UInt32,
    weekly_wage UInt32,
    contract_until Date
) ENGINE = MergeTree()
ORDER BY player_id;

CREATE TABLE IF NOT EXISTS capeverde.training_load (
    player_id UInt32,
    week_no UInt8,
    load_score Float32,
    fatigue_index Float32
) ENGINE = MergeTree()
ORDER BY (player_id, week_no);

CREATE TABLE IF NOT EXISTS capeverde.formations (
    formation_id UInt32,
    name String,
    players_json String,
    notes String,
    suitable_vs String
) ENGINE = MergeTree()
ORDER BY formation_id;

CREATE TABLE IF NOT EXISTS capeverde.clubs (
    club_id UInt32,
    name String,
    league String
) ENGINE = MergeTree()
ORDER BY club_id;

CREATE TABLE IF NOT EXISTS capeverde.trophies (
    trophy_id UInt32,
    name String,
    year UInt16
) ENGINE = MergeTree()
ORDER BY trophy_id;

CREATE TABLE IF NOT EXISTS capeverde.matches (
    match_id UInt32,
    opponent String,
    date Date,
    result String,
    goals_for UInt8,
    goals_against UInt8
) ENGINE = MergeTree()
ORDER BY match_id;
