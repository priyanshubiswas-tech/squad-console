-- Master database: holds all 7 teams together, partitioned by team_code.
-- Every table carries a team_code column (even ones that conceptually belong
-- to a single player) so ingestion/partition.py can fan rows out into the
-- per-team databases with a plain `WHERE team_code = '{code}'` per table.

CREATE DATABASE IF NOT EXISTS squad_data_store;

CREATE TABLE IF NOT EXISTS squad_data_store.players (
    player_id UInt32,
    name String,
    position String,
    club String,
    age UInt8,
    overall_rating UInt8,
    nationality String,
    photo_url String,
    team_code String,
    source String        -- data provenance, e.g. 'real:wikipedia' or 'synthetic' - see /api/data-sources
) ENGINE = MergeTree()
PARTITION BY team_code
ORDER BY (team_code, player_id);

CREATE TABLE IF NOT EXISTS squad_data_store.public_stats (
    player_id UInt32,
    goals UInt16,
    assists UInt16,
    key_passes UInt16,
    tackles UInt16,
    rating_avg Float32,
    matches_played UInt16,
    team_code String
) ENGINE = MergeTree()
PARTITION BY team_code
ORDER BY (team_code, player_id);

CREATE TABLE IF NOT EXISTS squad_data_store.injuries (
    player_id UInt32,
    injury_type String,
    status String,
    expected_return Date,
    severity String,
    team_code String
) ENGINE = MergeTree()
PARTITION BY team_code
ORDER BY (team_code, player_id);

CREATE TABLE IF NOT EXISTS squad_data_store.salaries (
    player_id UInt32,
    weekly_wage UInt32,
    contract_until Date,
    team_code String
) ENGINE = MergeTree()
PARTITION BY team_code
ORDER BY (team_code, player_id);

CREATE TABLE IF NOT EXISTS squad_data_store.training_load (
    player_id UInt32,
    week_no UInt8,
    load_score Float32,
    fatigue_index Float32,
    team_code String
) ENGINE = MergeTree()
PARTITION BY team_code
ORDER BY (team_code, player_id, week_no);

CREATE TABLE IF NOT EXISTS squad_data_store.formations (
    formation_id UInt32,
    name String,
    players_json String,
    notes String,
    suitable_vs String,
    team_code String
) ENGINE = MergeTree()
PARTITION BY team_code
ORDER BY (team_code, formation_id);

CREATE TABLE IF NOT EXISTS squad_data_store.clubs (
    club_id UInt32,
    name String,
    league String,
    team_code String
) ENGINE = MergeTree()
PARTITION BY team_code
ORDER BY (team_code, club_id);

CREATE TABLE IF NOT EXISTS squad_data_store.trophies (
    trophy_id UInt32,
    name String,
    year UInt16,
    team_code String
) ENGINE = MergeTree()
PARTITION BY team_code
ORDER BY (team_code, trophy_id);

CREATE TABLE IF NOT EXISTS squad_data_store.matches (
    match_id UInt32,
    opponent String,
    date Date,
    result String,
    goals_for UInt8,
    goals_against UInt8,
    team_code String
) ENGINE = MergeTree()
PARTITION BY team_code
ORDER BY (team_code, match_id);
