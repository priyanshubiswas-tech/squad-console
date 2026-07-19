# backend

FastAPI service. Session, dashboard, inspect, data-sources, chart, report, and chat (LangGraph agent) routers are all built and access-controlled; only `news` remains for a later phase (see the root `README.md` roadmap).

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
- `GET /api/reports/fitness` 🔑, `/top-performers` 🔑, `/financial` 🔑 — the 3 chatbot "chips". Always scoped to the active team (cookie), no `{team_code}` path param. Each returns `{text, chart_url}` — a **fixed text template with live numbers** (never LLM-generated) plus a matplotlib/seaborn PNG. See `app/reports/generators.py` for the query + templating logic.
- `POST /api/chat` 🔑 — body `{"message": "..."}`, runs the full LangGraph agent (`app/langgraph_app/graph.py`) and returns `{text, chart_url}` — the exact same shape as the reports above, so the frontend renders a chip click and an LLM answer through one identical code path. That equivalence is the "hybrid" in this project's name.

`access_control.py` is the single function (`get_allowed_tables`) both `inspect.py` and the LangGraph `access_filter` node call — never duplicate that logic elsewhere. It's a separate concern from the `X-API-Key` gate above: the key controls whether a request reaches the API at all, the access-control matrix controls which data a legitimate request can see.

## The LangGraph agent (`app/langgraph_app/`)

Seven nodes, in order, matching the original spec exactly:

```
intent_router → stats_tool → rag_retriever → access_filter → reasoner → [chart_node?] → composer
```

- **`intent_router`** — keyword-based (no LLM), classifies `tactical_advice`/`comparison`/`stat_lookup`/`general` and extracts an opponent team name from phrasing like "vs Brazil". Keyword-based on purpose: intent routing works even with no LLM key.
- **`stats_tool`** — queries ClickHouse: own team's `players`/`public_stats`/`formations` in full; an opponent (if named) gets `public_stats` only.
- **`rag_retriever`** — queries ChromaDB: `{active_team}_full` always, plus `{opponent_team}_public` + `shared_theory` if an opponent was named. Never queries `{opponent_team}_full`.
- **`access_filter`** — re-applies `access_control.get_allowed_tables` as a defense-in-depth check on whatever the two nodes above fetched for an opponent.
- **`reasoner`** — the only node that needs an LLM (`ChatAnthropic`/`ChatOpenAI` via `langchain`). **Gracefully degrades** to an honest "no LLM key configured, try a chip instead" message if `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` is blank, rather than erroring — every upstream node still ran against real data either way.
- **`chart_node`** (conditional on `comparison` intent) — calls `app/charts/generators.py::team_comparison_chart`, the *same* function a chip could call. Chart generation never depends on the LLM.
- **`composer`** — assembles `{text, chart_url}`.

Test prompts to try once you've hit `POST /api/session/select-team`:
- *"What formation should I use against Brazil and why?"* → `tactical_advice`, retrieves `england_full` + `brazil_public` + `shared_theory`.
- *"Who are my top scorers?"* → `stat_lookup`, no opponent extracted.
- *"Compare my midfield to Brazil's"* → `comparison`, triggers `chart_node`, returns a real chart even without an LLM key.
- *"What's Brazil's injury situation?"* → `stats_tool` never queries opponent injuries at all (only `public_stats`), so this is structurally impossible to leak, not just prompt-filtered.

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
