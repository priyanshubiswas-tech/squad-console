# backend (FastAPI)

**Status**: session/dashboard/inspect/data-sources/charts all built and working. `news` and `chat` (LangGraph) are next-phase placeholders.

Lives in `../../backend/`. Currently exposes:
- `GET /api/health`, `GET /api/health/clickhouse` — liveness.
- `POST /api/session/select-team` — sets the `X-Active-Team` httpOnly cookie every other endpoint reads.
- `GET /api/dashboard/{team}` — full data, own team only (403 otherwise).
- `GET /api/inspect/{team}` — any team, filtered through [[access-control]]'s `get_allowed_tables`.
- `GET /api/data-sources` — real-vs-synthetic transparency breakdown for the frontend UI.
- `GET /api/charts/{team}/injury-risk` (private, active-team-only), `/top-performers` (public) — server-rendered matplotlib PNGs via `app/charts/generators.py`, callable directly with zero LLM involvement. This is the deterministic half of the planned "hybrid" chat design - chat-panel chips call these routes directly; the future [[langgraph-agent]]'s `chart_node` will call the *same* generator functions for free-form questions.
- `GET /api/charts/file/{filename}` — serves a generated PNG.

## Planned
- `chat` — thin wrapper around [[langgraph-agent]].
- `news` — surfaces [[newsapi-rss]] data.

Talks to [[clickhouse]] directly for dashboard/inspect/charts, and will talk to [[langgraph-agent]] for chat. Sits behind [[nginx]] once that's built; talked to directly on `localhost:8000` until then.

← back to [[index]]
