# ClickHouse

**Status**: schema built (this pass), empty — no data loaded yet.

The analytical store. See `../../database/clickhouse/README.md` for the actual DDL and SOPs; this note is about how it connects to everything else.

## Databases
- `squad_data_store` — master, `PARTITION BY team_code`, every table carries a `team_code` column so [[ingestion]]'s `partition.py` can fan rows out with a flat `WHERE team_code = '{code}'`.
- `england` / `france` / `brazil` / `argentina` / `spain` / `germany` / `portugal` — one per team, same table shapes minus `team_code` (except `players`) and minus partitioning.

## Who writes to it
- [[ingestion]] — the only writer. Loads fetched/mock JSON into the master DB, then fans out.

## Who reads from it
- [[backend-fastapi]] — dashboard/inspect endpoints read the active team's DB directly; cross-team queries (if any) hit the master DB.
- [[langgraph-agent]]'s `stats_tool` node — own team full read, opponent team `public_stats`-only read, gated by [[access-control]].

## Persistence
Named Docker volume `clickhouse_data`. Survives `docker compose stop/start`; only `down -v` wipes it. Schema self-creates once via ClickHouse's `/docker-entrypoint-initdb.d/` convention (see `database/clickhouse/init/`).

← back to [[index]]
