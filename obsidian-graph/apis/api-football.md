# API-Football

**Status**: not wired up yet — placeholder for the ingestion phase.

Free tier via RapidAPI, 100 requests/day. Source of player stats, fixtures, standings, and partial injury coverage.

- Feeds into: [[ingestion]] → [[clickhouse]] (`public_stats`, `matches`, and partial `injuries`)
- Env var: `API_FOOTBALL_KEY` in `.env`
- Caching: results must be cached aggressively in ClickHouse — the free tier's daily cap can't sustain live queries per request.
- Gaps this API doesn't cover: injury detail, salaries, training load, tactics — see [[ingestion]] for how those get synthesized instead.

← back to [[index]]
