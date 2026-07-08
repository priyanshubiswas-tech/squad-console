# backend

FastAPI service. Session, dashboard, inspect, data-sources, and chart routers are built and access-controlled; `news` and the LangGraph `chat` endpoint come in a later phase (see the root `README.md` roadmap).

## Endpoints

- `GET /api/health` — liveness check.
- `GET /api/health/clickhouse` — runs `SELECT 1` against ClickHouse and confirms the master DB + all 7 team DBs exist.
- `POST /api/session/select-team` — body `{"team_code": "england"}`, sets the `X-Active-Team` httpOnly cookie every other endpoint reads, returns `{team_code, manager_name}`.
- `GET /api/dashboard/{team_code}` — full squad data. 403 if `team_code` isn't the active team (cookie) — own-team-only, no exceptions.
- `GET /api/inspect/{team_code}` — any team's data, filtered through `access_control.get_allowed_tables`: `injuries`/`salaries`/`training_load` come back `null` (present, not omitted), `formations` is stripped to `name`/`suitable_vs`.
- `GET /api/data-sources` — which fields are real (and cited) vs. synthetic (and why), for the frontend's transparency UI.
- `GET /api/charts/{team_code}/injury-risk` — private, active-team-only (403 otherwise) — matplotlib PNG of the squad's fatigue trend.
- `GET /api/charts/{team_code}/top-performers` — public, any team — matplotlib PNG of top `rating_avg` players.
- `GET /api/charts/file/{filename}` — serves a previously generated chart PNG.

`access_control.py` is the single function (`get_allowed_tables`) both `inspect.py` and the future LangGraph `access_filter` node call — never duplicate that logic elsewhere.

## Local development (without Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Requires `CLICKHOUSE_HOST` in your environment to point at wherever ClickHouse is actually reachable (e.g. `localhost` if you're running outside Docker but ClickHouse is exposed on the host).
