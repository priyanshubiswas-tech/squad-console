# Architecture

`squad-console` is a national-team manager console: a manager logs in by picking their federation crest (no typing, no auth), sees a full dashboard of their own squad, can "inspect" the other 6 teams with private fields redacted, and can ask a RAG-backed chatbot tactical questions that respect the same privacy rules. See `diagrams.md` for the visual version of everything below.

## Layers

1. **External data + mock generators** — Wikipedia (real, built) for full 26-man squads, TheSportsDB (real, free tier, built) for photos/matches; API-Football, Transfermarkt, RSS/NewsAPI still to come (need paid/signup keys). Synthetic generators cover data with no free source (injury detail, salaries, training load, tactics), keyed to real player ids so they attach to actual squad members. See `../ingestion/README.md` for exactly what's real vs. synthetic today.
2. **Ingestion layer** — currently a host-run Python script (`ingestion/elt-pipeline-py-script/deploy_elt.py`), run manually, not yet scheduled. Extract writes raw API responses into ClickHouse's `raw_data_store` (audit trail); Transform/mock-generate load `squad_data_store` (master); Partition fans it out into the 7 per-team databases (truncate-and-reload). Each stage is an independent function specifically so it can become its own Airflow task later, once real-time/scheduled refresh matters.
3. **Analytical store (ClickHouse)** — `squad_data_store` (master, partitioned by `team_code`), `raw_data_store` (raw landing zone), plus one database per team (`england`, `france`, `brazil`, `argentina`, `spain`, `germany`, `portugal`) — schema built and populated with real, full squads. See `../database/clickhouse/README.md`.
4. **RAG layer (ChromaDB + embedding job)** — built. Real, researched per-team knowledge base markdown (`tactics_notes.md`, `public_scouting.md`) plus a shared tactical-theory doc, chunked and embedded via `embedding_job/embed_team_docs.py` (host-run) into 15 Chroma collections with `{team, doc_type, visibility}` metadata, using a local sentence-transformers model - no LLM key needed for this phase. Not yet queried by anything (that's the agent layer below).
5. **Agent layer (LangGraph)** — a 7-node graph (`intent_router → stats_tool → rag_retriever → access_filter → reasoner → [chart_node?] → composer`) that answers tactical questions using the active team's full data plus the opponent's public data only. The `access_filter` node is the single enforcement point — it re-applies the same `access_control.py` function the REST API already uses (see below), so there is one source of truth for what's private. Not built yet — this is the last phase, and the only one that needs an LLM key. Its deterministic sibling **is** built: `backend/app/reports/generators.py` implements the same "query ClickHouse → produce `{text, chart_url}`" contract as 3 fixed-template, zero-LLM chatbot "chips" (`/api/reports/fitness`, `/top-performers`, `/financial`), calling the same `backend/app/charts/generators.py` chart functions the future `chart_node` will call. See the root README's "The hybrid chat design" section.
6. **Serving layer (FastAPI + Nginx)** — FastAPI exposes REST endpoints with access control: `session`, `dashboard`, `inspect`, `data-sources`, `charts`, `reports` are built (`../backend/`); `chat`/LangGraph comes next. Nginx is built and in the compose stack (`../nginx/`) as the reverse proxy, enforcing a shared `X-API-Key` secret in front of the backend - the backend independently re-checks the same key, since its port is still published directly to the host for dev convenience (see the root README's "Nginx + API key gate" section for the full reasoning). This key is a separate concern from `access_control.py` above: the key gates *access to the API at all*, the access-control matrix gates *which data a legitimate, keyed request can see*.
7. **Frontend (React + Tailwind)** — the only place the public product name/branding is meant to live. Minimal placeholder built (`../frontend/`) — proves it can reach the backend/ClickHouse over Docker networking; no real pages yet, though the backend API they'll call is ready.

## Access control (single source of truth)

`backend/app/access_control.py`, one function — `get_allowed_tables(requested_team, active_team)` — decides what's visible. `backend/app/routers/inspect.py` already calls it; the LangGraph `access_filter` node will call the same function once it exists. Never duplicate this logic.

This is also the app's actual value proposition (see the root README's "The product: public vs. private data"): public data is what the press/a rival federation could already know, private data is your own coaching staff's internal intelligence.

| Table | Own team (active) | Other team (inspect mode) |
|---|---|---|
| `players` (basic fields) | full | full |
| `public_stats` | full | full |
| `clubs`, `trophies`, `matches` | full | full |
| `injuries` | full | **null** (blocked) |
| `salaries` | full | **null** (blocked) |
| `training_load` | full | **null** (blocked) |
| `formations` | full | `name` + `suitable_vs` only |

Private fields are always returned as `null`, never omitted — the frontend needs the key present to render a blur placeholder rather than treating the section as absent.

## Naming

The product's public name is intentionally kept out of everything except the frontend (`../frontend/`), so it can change without touching infra: Docker network `squadnet`, ClickHouse master DB `squad_data_store`, project name `squad-console`. Team codes (`england`, `brazil`, ...) aren't brand names, so they're used freely everywhere.

## Design system (for when the frontend is built)

Dark football theme — background `#0a0e14`, panels `#121826`, cards `#171f30`, card hover `#1c2740`. Pitch-green accent `#22c55e` (recommended/positive), night-indigo accent `#6366f1` (identity/avatars/active nav), danger red `#ef4444` (injuries), amber `#facc15` (lock/private indicator). Each team gets a header-gradient accent pair drawn from its kit colors. Cards: 12px radius, 1px `#2a3344` borders, no heavy shadows.

## Roadmap

See the root `README.md` for the phase-by-phase build order this repo follows.
