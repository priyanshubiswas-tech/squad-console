# backend

FastAPI service. Currently just a health-check base — routers for `session`, `dashboard`, `inspect`, `news`, `chat`, and the LangGraph app get added in later phases (see the root `README.md` roadmap).

## Endpoints

- `GET /api/health` — liveness check.
- `GET /api/health/clickhouse` — runs `SELECT 1` against ClickHouse and confirms the master DB + all 7 team DBs exist.

## Local development (without Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Requires `CLICKHOUSE_HOST` in your environment to point at wherever ClickHouse is actually reachable (e.g. `localhost` if you're running outside Docker but ClickHouse is exposed on the host).
