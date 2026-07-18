# backend (FastAPI)

**Status**: session/dashboard/inspect/data-sources/charts/reports all built and working. `news` and `chat` (LangGraph) are next-phase placeholders.

Lives in `../../backend/`. Currently exposes:
- `GET /api/health`, `GET /api/health/clickhouse` — liveness.
- `POST /api/session/select-team` — sets the `X-Active-Team` httpOnly cookie every other endpoint reads.
- `GET /api/dashboard/{team}` — full data, own team only (403 otherwise).
- `GET /api/inspect/{team}` — any team, filtered through [[access-control]]'s `get_allowed_tables`.
- `GET /api/data-sources` — real-vs-synthetic transparency breakdown for the frontend UI.
- `GET /api/charts/{team}/injury-risk` (private, active-team-only), `/top-performers` (public) — server-rendered matplotlib/seaborn PNGs via `app/charts/generators.py`, callable directly with zero LLM involvement.
- `GET /api/charts/file/{filename}` — serves a generated PNG.
- `GET /api/reports/fitness`, `/top-performers`, `/financial` — the 3 chatbot "chips" (`app/reports/generators.py`). Always scoped to the active team (cookie). Fixed text template + live ClickHouse numbers + a chart, returned as `{text, chart_url}` - the exact shape [[langgraph-agent]]'s composer will use, so a chip click and an LLM answer render through one identical frontend path. See [[chat-request-flow]] for how this sits alongside the LLM path.

## Planned
- `chat` — thin wrapper around [[langgraph-agent]]; its `chart_node` calls the *same* `app/charts/generators.py` functions the reports above use.
- `news` — surfaces [[newsapi-rss]] data.

Talks to [[clickhouse]] directly for dashboard/inspect/charts, and will talk to [[langgraph-agent]] for chat. Sits behind [[nginx]] once that's built; talked to directly on `localhost:8000` until then.

← back to [[index]]
