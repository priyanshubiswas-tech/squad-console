-- Raw landing zone: every external API response gets dumped here, byte-for-byte,
-- before any parsing/cleaning happens. This is the audit trail - if a transform
-- script has a bug, you can always re-run it against exactly what the API
-- returned, without re-fetching. Append-only: never truncated by ingestion.

CREATE DATABASE IF NOT EXISTS raw_data_store;

CREATE TABLE IF NOT EXISTS raw_data_store.thesportsdb_dumps (
    fetched_at DateTime,
    team_code String,
    entity String,       -- 'team' | 'squad' | 'matches'
    source_url String,
    payload String        -- raw JSON response body, untouched
) ENGINE = MergeTree()
ORDER BY (team_code, entity, fetched_at);
