# ingestion

**Status**: not built yet — next phase after this infra pass.

Python + APScheduler container. Two families of sources feed it, on purpose producing the *same JSON shape* so one is a drop-in replacement for the other:
- Real fetchers: [[api-football]], [[thesportsdb]], [[transfermarkt]], [[newsapi-rss]]
- Mock generators: synthetic data for anything with no free source — injury detail, salaries, training load, tactics/formations notes.

Runs on a fixed interval (`INGESTION_INTERVAL_HOURS` in `.env`), writes into [[clickhouse]]'s master DB, then runs `partition.py` to fan rows into the 7 per-team DBs (truncate-and-reload).

← back to [[index]]
