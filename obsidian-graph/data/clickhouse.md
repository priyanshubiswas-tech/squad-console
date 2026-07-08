# ClickHouse

**Status**: schema built, populated with real (full 26-man squads) + synthetic data via [[ingestion]].

The analytical store. See `../../database/clickhouse/README.md` for the actual DDL and SOPs; this note is about how it connects to everything else.

## Databases
- `squad_data_store` — master, `PARTITION BY team_code`, every table carries a `team_code` column so [[ingestion]]'s `partition.py` can fan rows out with a flat `WHERE team_code = '{code}'`.
- `england` / `france` / `brazil` / `argentina` / `spain` / `germany` / `portugal` — one per team, same table shapes minus `team_code` (except `players`) and minus partitioning.
- `raw_data_store` — append-only landing zone for raw API responses, byte-for-byte, before parsing. [[ingestion]]'s transform stages read the latest dump per team/entity from here rather than in-memory from the fetch stage, so the two stay decoupled (and can become separate Airflow tasks later).

## Who writes to it
- [[ingestion]] — the only writer. Dumps raw JSON into `raw_data_store`, transforms/generates into the master DB, then fans out.

## Who reads from it
- [[backend-fastapi]] — dashboard/inspect/charts endpoints read the active team's DB directly, gated by [[access-control]].
- [[langgraph-agent]]'s `stats_tool` node (not built yet) — own team full read, opponent team `public_stats`-only read, gated by the same [[access-control]] function.

## Persistence
Named Docker volume `clickhouse_data`. Survives `docker compose stop/start`; only `down -v` wipes it. Schema self-creates once via ClickHouse's `/docker-entrypoint-initdb.d/` convention (see `database/clickhouse/init/`).

← back to [[index]]
