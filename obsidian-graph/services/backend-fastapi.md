# backend (FastAPI)

**Status**: session/dashboard/inspect/data-sources/charts/reports/chat all built and working. Only `news` remains.

Lives in `../../backend/`. Currently exposes:
- `GET /api/health`, `GET /api/health/clickhouse` — liveness.
- `POST /api/session/select-team` — sets the `X-Active-Team` httpOnly cookie every other endpoint reads.
- `GET /api/dashboard/{team}` — full data, own team only (403 otherwise).
- `GET /api/inspect/{team}` — any team, filtered through [[access-control]]'s `get_allowed_tables`.
- `GET /api/data-sources` — real-vs-synthetic transparency breakdown for the frontend UI.
- `GET /api/charts/{team}/injury-risk` (private, active-team-only), `/top-performers` (public) — server-rendered matplotlib/seaborn PNGs via `app/charts/generators.py`, callable directly with zero LLM involvement.
- `GET /api/charts/file/{filename}` — serves a generated PNG.
- `GET /api/reports/fitness`, `/top-performers`, `/financial` — the 3 chatbot "chips" (`app/reports/generators.py`). Always scoped to the active team (cookie). Fixed text template + live ClickHouse numbers + a chart, returned as `{text, chart_url}`.
- `POST /api/chat` — runs the full [[langgraph-agent]] graph, returns `{text, chart_url}` - the exact same shape the reports above use, so a chip click and an LLM answer render through one identical frontend path. See [[chat-request-flow]].

## Planned
- `news` — surfaces [[newsapi-rss]] data.

Talks to [[clickhouse]] directly for dashboard/inspect/charts/reports, and to [[chromadb]] + [[clickhouse]] via [[langgraph-agent]] for chat. Sits behind [[nginx]]; still also reachable directly on `localhost:8000` (dev convenience, both independently check `X-API-Key`).

← back to [[index]]
