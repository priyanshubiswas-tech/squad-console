# backend

FastAPI service. Session, dashboard, inspect, data-sources, chart, and report routers are built and access-controlled; `news` and the LangGraph `chat` endpoint come in a later phase (see the root `README.md` roadmap).

## Endpoints

`🔑` = requires an `X-API-Key` header matching `.env`'s `API_KEY` (checked here even though Nginx also checks it — see the root README's "Nginx + API key gate").

- `GET /api/health` — liveness check.
- `GET /api/health/clickhouse` — runs `SELECT 1` against ClickHouse and confirms the master DB + all 7 team DBs exist.
- `POST /api/session/select-team` 🔑 — body `{"team_code": "england"}`, sets the `X-Active-Team` httpOnly cookie every other endpoint reads, returns `{team_code, manager_name}`.
- `GET /api/dashboard/{team_code}` 🔑 — full squad data. 403 if `team_code` isn't the active team (cookie) — own-team-only, no exceptions.
- `GET /api/inspect/{team_code}` 🔑 — any team's data, filtered through `access_control.get_allowed_tables`: `injuries`/`salaries`/`training_load` come back `null` (present, not omitted), `formations` is stripped to `name`/`suitable_vs`.
- `GET /api/data-sources` 🔑 — which fields are real (and cited) vs. synthetic (and why), for the frontend's transparency UI.
- `GET /api/charts/{team_code}/injury-risk` 🔑 — private, active-team-only (403 otherwise) — matplotlib PNG of the squad's fatigue trend.
- `GET /api/charts/{team_code}/top-performers` 🔑 — public, any team — matplotlib PNG of top `rating_avg` players.
- `GET /api/charts/file/{filename}` — serves a previously generated chart PNG. Deliberately not key-gated: it's loaded via a plain `<img src>`, which can't attach custom headers, and the private data behind it was already access-controlled when the chart was generated.
- `GET /api/reports/fitness` 🔑, `/top-performers` 🔑, `/financial` 🔑 — the 3 chatbot "chips". Always scoped to the active team (cookie), no `{team_code}` path param. Each returns `{text, chart_url}` — a **fixed text template with live numbers** (never LLM-generated) plus a matplotlib/seaborn PNG. This is the same response shape the future LangGraph chat endpoint will return, so the frontend chat window renders a chip click and an LLM answer through one identical code path — that's the "hybrid" in this project's name. See `app/reports/generators.py` for the query + templating logic.

`access_control.py` is the single function (`get_allowed_tables`) both `inspect.py` and the future LangGraph `access_filter` node call — never duplicate that logic elsewhere. It's a separate concern from the `X-API-Key` gate above: the key controls whether a request reaches the API at all, the access-control matrix controls which data a legitimate request can see.

### On "parameterized queries" for a per-database-per-tenant model

This app's multi-tenancy is one ClickHouse **database** per team, not a `tenant_id` column - so the team can't be bound as a normal query parameter (SQL parameter binding targets *values*, never table/database identifiers, in ClickHouse or any SQL engine). `team_code` is interpolated directly into the SQL string in `app/reports/generators.py` and `app/charts/generators.py` - safe only because it has already passed `get_active_team`'s check against `settings.team_list` (see `app/deps.py`), never raw user input. Where a query filters by an actual value instead (e.g. `top_performers_report`'s `LIMIT`), that value **is** bound as a real ClickHouse parameter (`{limit:UInt8}` / `parameters={"limit": 5}`) - both patterns sit side by side in that function for the contrast.

## Local development (without Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Requires `CLICKHOUSE_HOST` in your environment to point at wherever ClickHouse is actually reachable (e.g. `localhost` if you're running outside Docker but ClickHouse is exposed on the host).
