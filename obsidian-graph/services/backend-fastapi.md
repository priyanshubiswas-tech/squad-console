# backend (FastAPI)

**Status**: health-check base built this pass. Session/dashboard/inspect/news/chat routers are next-phase placeholders.

Lives in `../../backend/`. Currently exposes:
- `GET /api/health` — liveness.
- `GET /api/health/clickhouse` — confirms [[clickhouse]]'s master DB + all 7 team DBs exist.

## Planned routers
- `session` — team selection, sets the `X-Active-Team` cookie that scopes every other read.
- `dashboard` — full data for the active team.
- `inspect` — other teams' data, redacted per [[access-control]].
- `chat` — thin wrapper around [[langgraph-agent]].
- `news` — surfaces [[newsapi-rss]] data.

Talks to [[clickhouse]] directly for dashboard/inspect, and to [[langgraph-agent]] for chat. Sits behind [[nginx]] once that's built; talked to directly on `localhost:8000` until then.

← back to [[index]]
