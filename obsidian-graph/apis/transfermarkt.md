# Transfermarkt (self-hosted API wrapper)

**Status**: not wired up yet — placeholder for the ingestion phase.

Self-hosted OSS wrapper (`transfermarkt-api`) around Transfermarkt data. Used as a proxy for market value / squad depth — the closest free substitute for real salary data, since actual wages aren't publicly available anywhere free.

- Feeds into: [[ingestion]] → [[clickhouse]] (`clubs`, informs but doesn't replace `salaries`)
- Env var: `TRANSFERMARKT_API_BASE` in `.env` (points at the wrapper's own container once it exists)
- Note: real `salaries`/`training_load`/tactics detail stays synthetic even after this API is wired up — see [[ingestion]].

← back to [[index]]
