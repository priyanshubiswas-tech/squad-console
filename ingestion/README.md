# ingestion (placeholder)

Not built yet. This will hold the uniform data-fetching layer: one Python fetcher per free API (API-Football, TheSportsDB, Transfermarkt, RSS/NewsAPI) plus synthetic generators for data with no free source (injuries detail, salaries, training load, tactics). Every fetcher will output the same JSON shape regardless of source, and a `partition.py` script will load that JSON into ClickHouse's master DB and fan it out into the 7 per-team DBs.

See `[[obsidian-graph/services/ingestion]]` for the design notes once they exist, and the root `README.md` roadmap for sequencing.
