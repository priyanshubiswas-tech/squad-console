# Architecture

`squad-console` is a national-team manager console: a manager logs in by picking their federation crest (no typing, no auth), sees a full dashboard of their own squad, can "inspect" the other 6 teams with private fields redacted, and can ask a RAG-backed chatbot tactical questions that respect the same privacy rules. See `diagrams.md` for the visual version of everything below.

## Layers

1. **External data + mock generators** — free football APIs (API-Football, TheSportsDB, Transfermarkt, RSS/NewsAPI) plus synthetic generators for data with no free source (injury detail, salaries, training load, tactics). Both paths are meant to converge on the *same JSON shape*, so swapping mock → real is a drop-in change. Not built yet — see the ingestion phase in the root README.
2. **Ingestion layer** — Python + APScheduler, runs on a fixed interval, loads fetched/generated JSON into ClickHouse's master database, then fans it out into 7 per-team databases (truncate-and-reload). Not built yet.
3. **Analytical store (ClickHouse)** — `squad_data_store` (master, partitioned by `team_code`) plus one database per team (`england`, `france`, `brazil`, `argentina`, `spain`, `germany`, `portugal`). Schema lives in `../database/clickhouse/init/` and is built out in this pass; population happens in the ingestion phase. See `../database/clickhouse/README.md`.
4. **RAG layer (ChromaDB + embedding job)** — per-team knowledge base markdown (tactics notes, public scouting reports) plus a shared tactical-theory doc, chunked and embedded into per-team Chroma collections with `{team, doc_type, visibility}` metadata. Not built yet.
5. **Agent layer (LangGraph)** — a 7-node graph (`intent_router → stats_tool → rag_retriever → access_filter → reasoner → [chart_node?] → composer`) that answers tactical questions using the active team's full data plus the opponent's public data only. The `access_filter` node is the single enforcement point — it re-applies the same access-control function the REST API uses, so there is one source of truth for what's private. Not built yet.
6. **Serving layer (FastAPI + Nginx)** — FastAPI exposes REST endpoints with access control; Nginx reverse-proxies `/api/*` to the backend and everything else to the built frontend. Only the FastAPI health-check base exists so far (`../backend/`); Nginx isn't in the compose stack yet — frontend and backend are reached directly on their own ports.
7. **Frontend (React + Tailwind)** — the only place the public product name/branding is meant to live. Minimal placeholder built (`../frontend/`) — proves it can reach the backend/ClickHouse over Docker networking; no real pages yet.

## Access control (single source of truth)

One function — `get_allowed_tables(requested_team, active_team)` — decides what's visible, and is used by both the REST "inspect" endpoint and the LangGraph `access_filter` node. Never duplicate this logic once it's built.

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
