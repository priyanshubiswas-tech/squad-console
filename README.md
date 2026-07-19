# squad-console

A national-team manager console: log in by tapping your federation's crest (no typing), see a full dashboard of your own squad, "inspect" the other 6 teams with private fields redacted, and ask a RAG-backed chatbot tactical questions that respect the same privacy rules. Built on FastAPI, ClickHouse, ChromaDB, LangGraph, React/Tailwind, and Docker Compose.

The public product name is intentionally kept **out of every layer except the frontend** — repo, services, database names, and code all use the neutral name `squad-console` so the brand can change later without touching infrastructure.

## Table of contents

- [Current status](#current-status)
- [Architecture](#architecture)
- [Repo layout](#repo-layout)
- [Prerequisites](#prerequisites)
- [Docker Compose setup SOP](#docker-compose-setup-sop)
- [What's already inside each container](#whats-already-inside-each-container)
- [Nginx + API key gate](#nginx--api-key-gate)
- [The hybrid chat design: 3 chips, zero LLM](#the-hybrid-chat-design-3-chips-zero-llm)
- [The product: public vs. private data](#the-product-public-vs-private-data)
- [Populating real data (ingestion)](#populating-real-data-ingestion)
- [Knowledge base + RAG (no LLM needed yet)](#knowledge-base--rag-no-llm-needed-yet)
- [Data persistence SOP](#data-persistence-sop)
- [Backing up and restoring ClickHouse data](#backing-up-and-restoring-clickhouse-data)
- [Adding your LLM API key later](#adding-your-llm-api-key-later)
- [Roadmap](#roadmap)

## Current status

Infrastructure base is up: four containers (ClickHouse, FastAPI backend, a placeholder React/Tailwind frontend, Nginx) on one Docker network, each independently health-checked, with persistent volumes for ClickHouse and generated charts. The frontend is still a minimal placeholder page — no login/dashboard/chat UI yet — but the **backend API is real and functional**:

- Every team has a **full, real 26-man squad** (Wikipedia's 2026 World Cup squads, cross-referenced with TheSportsDB for photos), plus real clubs/matches/trophies and synthetic values for fields with no free source — see [The product: public vs. private data](#the-product-public-vs-private-data).
- **Access control is implemented and enforced**, not just designed: `GET /api/dashboard/{team}` (full, own team only) and `GET /api/inspect/{team}` (redacted, any other team) both run through one shared `access_control.py`.
- **Charts render server-side and are callable directly** — `GET /api/charts/{team}/injury-risk` and `/top-performers` return a PNG URL with zero LLM involvement. This is the deterministic half of the "hybrid" chat design.
- **3 analyst "chip" reports are built and live** — `GET /api/reports/fitness`, `/top-performers`, `/financial` return a fixed text template with *live* stats plus a chart, in the exact shape the future LLM chat responses will use. See [The hybrid chat design](#the-hybrid-chat-design-3-chips-zero-llm).
- **Data provenance is a first-class API**, not just a doc comment — `GET /api/data-sources` tells you exactly which fields are real (and from where) vs. synthetic (and why).
- **Nginx is the front door with an API-key gate** — see [Nginx + API key gate](#nginx--api-key-gate).
- **The RAG corpus is written and embedded** — real, researched tactical dossiers for all 7 teams (formations, key-player dependencies, honest weaknesses) plus public scouting reports, chunked and embedded into ChromaDB with zero LLM calls (a local sentence-transformers model). See [Knowledge base + RAG](#knowledge-base--rag-no-llm-needed-yet).

No LLM key is configured yet — that's the last phase (the LangGraph agent itself, which reasons over what's now embedded), listed in [Roadmap](#roadmap).

## Architecture

See `architecture/ARCHITECTURE.md` for the full narrative and `architecture/diagrams.md` for the diagrams (high-level flow, chatbot request flow, container/persistence layout, access-control matrix). For a browsable map of how every API/service/data store connects, open `obsidian-graph/` as an Obsidian vault (or just read the markdown — it renders fine on GitHub too).

```mermaid
flowchart LR
    ext["Wikipedia + TheSportsDB (real) + mock generators"] --> raw["raw_data_store"]
    raw --> ingest["deploy_elt.py\n(host script)"]
    ingest --> ch["ClickHouse\nsquad_data_store + 7 team DBs"]
    kb["knowledge_base/\n(researched, real content)"] --> embed["embed_team_docs.py\n(host script)"]
    embed --> chroma["ChromaDB\n15 collections"]
    ch --> backend["FastAPI backend"]
    chroma -.->|"not wired up yet"| backend
    nginx["Nginx\nX-API-Key gate"] --> backend
    nginx --> frontend["Frontend (placeholder page)"]
```

## Repo layout

```
.
├── architecture/       # narrative + Mermaid diagrams
├── obsidian-graph/      # backlinked notes mapping how everything connects
├── database/clickhouse/ # schema (init/) + SOPs
├── backend/             # FastAPI app
├── ingestion/           # host-run ELT pipeline: real Wikipedia/TheSportsDB data + synthetic fields -> ClickHouse
├── embedding_job/       # host-run: chunks + embeds knowledge_base/ into ChromaDB, no LLM needed
├── knowledge_base/      # real, researched tactics/scouting content for all 7 teams + shared theory
├── frontend/            # minimal Vite+React+Tailwind placeholder — the only place brand name/UI lives
├── nginx/templates/     # reverse proxy + X-API-Key gate (envsubst template)
├── docker-compose.yml
├── .env.example
└── .env                 # your local copy, gitignored — never committed
```

## Prerequisites

- Docker Desktop (or another Docker Engine + Compose v2)
- That's it to run this pass — no Python/Node install needed locally, everything runs in containers.

## Docker Compose setup SOP

Five containers — `clickhouse`, `chroma`, `backend`, `frontend`, `nginx` — on one Docker network (`squadnet`), brought up together with a single `docker-compose.yml`. Steps below take you from a fresh clone to all five verified healthy.

**1. Clone and configure**

```bash
git clone <this-repo-url>
cd squad-console
cp .env.example .env       # already has working defaults; edit if you have API keys
```

**2. Build and start every container**

```bash
docker compose up -d --build
```

This creates, in order: the `squadnet` network → the `clickhouse_data`/`charts_data`/`chroma_data` named volumes → the `clickhouse` and `chroma` containers → the `backend` container (waits for both to report healthy) → the `frontend` container (waits for the backend) → the `nginx` container (waits for both, reverse-proxies everything behind the `X-API-Key` gate).

**3. Watch it come up**

```bash
docker compose ps
```

All five should settle on `Up ... (healthy)` within about 30 seconds on a first build (ClickHouse takes the longest — it's creating 9 databases). If `clickhouse` briefly shows `unhealthy` right after the very first boot, give it one restart: `docker compose restart clickhouse` (a known one-time race between its init-script bootstrap and the real server binding its ports — see `database/clickhouse/README.md`).

**4. Verify each service individually**

```bash
# ClickHouse — HTTP interface directly
curl "http://localhost:8123/ping"                                            # Ok.
curl "http://localhost:8123/?query=SHOW+DATABASES" --user default:changeme   # lists all 9 DBs

# Backend — FastAPI (direct, bypassing Nginx — still gated by its own X-API-Key check)
curl localhost:8000/api/health                                                    # {"status": "ok"}, no key needed
curl -H "X-API-Key: $(grep ^API_KEY= .env | cut -d= -f2)" localhost:8000/api/data-sources

# Through Nginx (port 80) — the real front door, same gate enforced again
curl -H "X-API-Key: $(grep ^API_KEY= .env | cut -d= -f2)" localhost/api/data-sources
curl localhost/                                                                    # frontend passthrough, no key needed

# Frontend — placeholder page (calls the backend health check itself, key baked in at build time)
open http://localhost:3000
```

**Common commands**

| Command | Effect |
|---|---|
| `docker compose up -d` | Start everything (build only if images don't exist yet) |
| `docker compose up -d --build` | Rebuild images first, then start — use after changing backend/frontend code or their Dockerfiles |
| `docker compose logs -f <service>` | Tail logs for one container (`clickhouse`, `backend`, or `frontend`) |
| `docker compose restart <service>` | Restart a single container without touching the others |
| `docker compose ps` | Show container status + health |
| `docker compose down` | Stop and remove containers (volume survives) |
| `docker compose down -v` | Stop and remove containers **and** the ClickHouse volume — destructive, see below |

## What's already inside each container

| Container | Image / base | Exposed on host | What's there right now |
|---|---|---|---|
| `clickhouse` | `clickhouse/clickhouse-server:24.8-alpine` | `8123` (HTTP), `9000` (native) | 9 databases: `squad_data_store` (master, partitioned by `team_code`), `raw_data_store` (raw API dump audit trail), + `england`/`france`/`brazil`/`argentina`/`spain`/`germany`/`portugal`. Each team DB has the 9 tables from `database/clickhouse/init/` (`players`, `public_stats`, `injuries`, `salaries`, `training_load`, `formations`, `clubs`, `trophies`, `matches`), **populated** — real squad/match/trophy data plus synthetic fields, via `ingestion/`. Default credentials from `.env` (`default` / `changeme` — change before this ever holds real *private* data). |
| `chroma` | `chromadb/chroma:0.5.20` | `8001` (→ container port `8000`) | 15 collections, **populated**: `{team}_full` (private tactics) + `{team}_public` (public scouting) for all 7 teams, plus `shared_theory`. Embedded via `embedding_job/` using a local sentence-transformers model — no LLM key involved. Not yet queried by the backend (that's the LangGraph agent phase). |
| `backend` | `python:3.12-slim` + FastAPI/uvicorn | `8000` | `GET /api/health`, `GET /api/health/clickhouse` — liveness, no key needed. `POST /api/session/select-team`, `GET /api/dashboard/{team}`, `GET /api/inspect/{team}`, `GET /api/data-sources`, `GET /api/charts/{team}/injury-risk`\|`/top-performers`, `GET /api/reports/fitness`\|`/top-performers`\|`/financial` — all require `X-API-Key`. `GET /api/charts/file/{filename}` — serves the PNG, no key (can't attach headers to `<img src>`; access control already happened at generation time). `chat`/LangGraph endpoint comes in the next phase. |
| `frontend` | `node:20-alpine` build → `nginx:alpine` serve | `3000` (→ container port `80`) | One static placeholder page (Vite + React + Tailwind) that calls the backend's ClickHouse health check (with `X-API-Key` attached) and renders the result. No login/dashboard/chat UI yet — the backend API above is ready for it. |
| `nginx` | `nginx:1.27-alpine` | `80` | Reverse proxy: `/api/*` → `backend:8000` (gated by the same `X-API-Key`, checked again independently), `/api/charts/file/*` → `backend:8000` (ungated, see above), everything else → `frontend:80`. Config is an envsubst template (`nginx/templates/default.conf.template`) so the real key never has to be hardcoded into a committed file. |

## Nginx + API key gate

A shared secret (`API_KEY` in `.env`) is checked **twice**, independently: once by Nginx before it ever proxies a request to the backend, and again by the backend itself via a FastAPI dependency (`require_api_key` in `app/deps.py`). Either check failing returns `401`.

- **Why check it twice?** Right now `backend`'s port `8000` (and `frontend`'s `3000`) are still published directly to the host for dev convenience, so Nginx isn't the *only* way in — without the backend's own check, hitting `:8000` directly would skip the gate entirely. In a real deployment you'd close those direct ports so Nginx is the sole entrypoint (see the Roadmap).
- **Which routes are gated:** everything except `GET /api/health*` (so Docker's own healthcheck, which calls this with no headers, keeps working) and `GET /api/charts/file/{filename}` (a plain `<img src>` can't attach a custom header — the private data behind that image was already access-controlled when the chart was generated).
- **How the secret reaches Nginx without being committed to git:** `nginx/templates/default.conf.template` contains a literal `${API_KEY}` placeholder; the official Nginx image auto-runs `envsubst` on any `*.template` file under `/etc/nginx/templates/` at container start, substituting from the container's own environment (`env_file: .env`). The rendered config is never written back to the repo.
- **How the frontend gets it:** Vite bakes `VITE_*` variables into the JS bundle at *build* time, so `docker-compose.yml` passes `API_KEY` in as a build arg (`VITE_API_KEY`) to the frontend's Dockerfile. Worth being honest about the limit here: **this is inherently visible in the shipped browser bundle** (confirmed — `grep` the built JS and the key is right there in plain text). It's a real gate against casual/automated direct API access (bots, scanners, curl-without-context), not a true secret-keeping boundary — a determined user can always read it out of their own browser. That's an inherent property of any client-side "key" in a public web app, not a bug in this implementation.

Generate your own key any time with `python3 -c "import secrets; print(secrets.token_hex(24))"` and drop it into `.env`'s `API_KEY`.

## The hybrid chat design: 3 chips, zero LLM

The planned chat UI is a chatbox at the bottom (free-form questions, answered by the LangGraph agent once it exists — needs an LLM key) with exactly **3 quick-reply "chips"** above it. Clicking a chip never touches an LLM — it hits one of 3 new REST endpoints that query ClickHouse directly and come back instantly:

| Chip | Endpoint | Data | Chart |
|---|---|---|---|
| 🏥 Fitness & Injury Risk | `GET /api/reports/fitness` | private (`training_load` + `injuries`) | fatigue trend line |
| ⭐ Top Performers | `GET /api/reports/top-performers` | public (`public_stats`) | rating bar chart |
| 💰 Financial Overview | `GET /api/reports/financial` | private (`salaries`) | wage bill bar chart |

Each returns `{"text": "...", "chart_url": "..."}` — a **fixed text template, never LLM-generated**, with the actual numbers pulled live from ClickHouse on every call (so re-clicking a chip after `deploy_elt.py` runs again shows updated stats). This is deliberately the *exact same shape* the LangGraph chat endpoint will return later, so the frontend renders a chip's answer and an LLM's answer through one identical code path — click a chip or type a question, same-looking chat bubble either way. That equivalence is the actual "hybrid" the project is named for.

**On the "one database per tenant" query pattern**: this schema is one ClickHouse database per team, not a `tenant_id` column, so the team name can't be bound as a normal SQL parameter (parameter binding targets values, never table/database identifiers). `app/reports/generators.py` and `app/charts/generators.py` interpolate `team_code` directly into the SQL string — safe only because every call site has already run it through `get_active_team`'s check against `settings.team_list` (`app/deps.py`), never raw user input. Where a query filters by an actual value instead (e.g. the top-5 `LIMIT` in the performers report), that value *is* bound as a real ClickHouse parameter (`{limit:UInt8}`) — see `backend/README.md` for the full explanation with both patterns side by side.

## The product: public vs. private data

This is the actual value proposition, not just an access-control exercise. It mirrors how a real federation is organized: **public** is whatever the press or a rival federation could already know; **private** is your own coaching staff's internal intelligence — nobody outside your building sees it.

| | Public (any team, yours or a rival's) | Private (your own team's staff only) |
|---|---|---|
| Squad | Real bio, real stats, real club, real photo (where available) | — |
| Medical | — | Injury type, severity, expected return |
| Financial | — | Weekly wage, contract expiry |
| Sports science | — | Weekly training load, fatigue trend, **injury-risk chart** (derived from that trend) |
| Tactics | Formation *name* only | Full lineup, tactical notes, set-piece detail |
| History | Clubs, trophies, match results | — |

Every private field is synthetic because no free (or, for `public_stats`, even paid-yet) data source exists for it — see `ingestion/README.md` for the full real-vs-synthetic table, and `GET /api/data-sources` for the same breakdown surfaced live in the product itself rather than buried in docs.

## Populating real data (ingestion)

`ingestion/elt-pipeline-py-script/` runs on the **host**, deliberately outside Docker, so it can be edited and re-run with no image/container involved. It pulls real, full 26-man squads from Wikipedia (cross-referenced with TheSportsDB for photos and match results), plus synthetic values for fields with no free source (see `ingestion/README.md` for exactly which is which), and loads all of it into every ClickHouse database. It connects to ClickHouse through the port already published to `localhost` — the `clickhouse` container must be running.

```bash
cd ingestion/elt-pipeline-py-script
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python deploy_elt.py
```

Every run is a full truncate-and-reload, so it's safe to re-run any time. Verify it worked:

```bash
docker compose exec clickhouse clickhouse-client --user default --password changeme \
  --query "SELECT name, position, club FROM england.players FORMAT PrettyCompact"
```

## Knowledge base + RAG (no LLM needed yet)

`knowledge_base/{team}/tactics_notes.md` (private) and `public_scouting.md` (public) are real, researched content for all 7 teams — not templated filler. Each covers the manager's actual tactical history and philosophy, concrete formation options naming real players by role, key-player dependencies ("what breaks if X is missing"), pressing/defensive shape, squad depth by position, individual player tactical traits, at least one honest exploitable weakness, and (for the public files) star names, trophy history, and the real World Cup 2026 campaign so far. `knowledge_base/shared/tactical_theory.md` is a team-agnostic glossary (high press, false nine, double pivot, etc.) every team file assumes familiarity with.

`embedding_job/` (host-run, like `ingestion/`) chunks these along markdown section headers and embeds them into ChromaDB using a **local sentence-transformers model** (`all-MiniLM-L6-v2`, downloaded once, ~80MB) — no LLM API call, no key needed:

```bash
docker compose up -d chroma
cd embedding_job
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python embed_team_docs.py
```

This produces 15 collections: `{team}_full` (private, `visibility: private` metadata), `{team}_public` (public), and `shared_theory`, mirroring the ClickHouse access-control split but for documents. Verify retrieval quality directly:

```bash
python3 -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8001)
coll = client.get_collection('england_full')
r = coll.query(query_texts=['what happens if a key defender is missing'], n_results=1)
print(r['documents'][0][0][:300])
"
```

Not wired into the backend yet — that's the LangGraph agent's `rag_retriever` node, the next and final phase before the app needs an LLM key.

## Data persistence SOP

- `docker compose stop` / `docker compose start` — **preserves** the ClickHouse, Chroma, and charts volumes. Safe to use any time.
- `docker compose down` (no flag) — stops and removes containers, but the named volumes survive; `docker compose up -d` afterwards picks up right where you left off.
- `docker compose down -v` — **destroys** the `clickhouse_data` volume and everything in it. Only use this if you actually want a clean slate (e.g. you changed a schema file under `database/clickhouse/init/` and need it to re-run).

## Backing up and restoring ClickHouse data

The data itself (as opposed to the schema, which is version-controlled SQL) lives only in the `clickhouse_data` Docker volume — it's not something that belongs in git (binary, changes constantly, would bloat the repo). To hand someone a working copy of your data, share a tarball of that volume instead. This is a raw filesystem-level backup, so it captures schema + data + everything together — whoever restores it doesn't need to run the init scripts separately.

**Owner: create a backup**

```bash
# Stop ClickHouse first so nothing is mid-write during the copy
docker compose stop clickhouse

docker run --rm \
  -v squad-console_clickhouse_data:/data \
  -v "$(pwd)":/backup \
  alpine tar czf /backup/clickhouse_data_backup.tar.gz -C /data .

docker compose start clickhouse
```

This produces `clickhouse_data_backup.tar.gz` in the repo root — share that file however you'd share any large file (it is **not** committed to git; keep it out of the repo).

**Recipient: restore a shared backup**

```bash
git clone <this-repo-url>
cd squad-console
cp .env.example .env

# Bring the stack up once so the named volume exists, then stop ClickHouse
docker compose up -d clickhouse
docker compose stop clickhouse

# Drop the shared clickhouse_data_backup.tar.gz into the repo root, then:
docker run --rm \
  -v squad-console_clickhouse_data:/data \
  -v "$(pwd)":/backup \
  alpine sh -c "rm -rf /data/* && tar xzf /backup/clickhouse_data_backup.tar.gz -C /data"

docker compose up -d
```

Verify it worked with the same health checks from the setup SOP above (`curl localhost:8000/api/health/clickhouse` should now show row counts once data exists, not just empty schema). The volume name is fixed by the compose project name (`squad-console_clickhouse_data`) — if you renamed the project in `docker-compose.yml`'s top-level `name:` field, adjust the volume name in these commands to match (`docker volume ls` shows the actual name).

## Adding your LLM API key later

This project runs fully on real + synthetic data with **no LLM key** for now — that gets added last, once the LangGraph agent phase is built. When you get there: open `.env`, fill in `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` plus `LLM_MODEL`, and restart the backend (`docker compose restart backend`). Nothing else changes.

## Roadmap

Phases still to come, in order:

1. ~~**Uniform data ingestion**~~ — done: real 26-man squads (Wikipedia + TheSportsDB), matches, trophies, plus synthetic fields, via `ingestion/elt-pipeline-py-script/deploy_elt.py`. Still open: API-Football (real `public_stats`, needs a paid key), Transfermarkt/RSS fetchers, and an Airflow layer to schedule/automate re-fetching instead of running `deploy_elt.py` by hand.
2. ~~**Access control + REST API**~~ — done: `access_control.py` (single source of truth), `session`/`dashboard`/`inspect` routers, `data-sources` transparency endpoint.
3. ~~**Charts (deterministic half)**~~ — done: `backend/app/charts/generators.py` + `/api/charts/*` router, callable directly with zero LLM involvement — this is the non-agentic half of the "hybrid" chat design.
4. ~~**Nginx + API key gate**~~ — done: reverse proxy in front of backend + frontend, `X-API-Key` enforced independently by both Nginx and the backend. Still open: closing the direct `8000`/`3000` host ports so Nginx is the *only* way in (kept open for now, dev convenience).
5. ~~**3 chip reports (deterministic chat half)**~~ — done: `backend/app/reports/generators.py` + `/api/reports/*` router — fixed text templates with live ClickHouse stats, matching the exact `{text, chart_url}` shape the LangGraph chat endpoint will return. See "The hybrid chat design" above.
6. ~~**RAG pipeline**~~ — done: real, researched `knowledge_base/` content for all 7 teams + shared theory, chunked and embedded into 15 ChromaDB collections via `embedding_job/` (local sentence-transformers model, no LLM key). Not yet queried by the backend.
7. **Agentic layer (agentic half of "hybrid", last phase before an LLM key is needed)** — LangGraph agent (`backend/app/langgraph_app/`), wired to a `chat` endpoint: `intent_router → stats_tool → rag_retriever → access_filter → reasoner → chart_node → composer`. `rag_retriever` queries the ChromaDB collections built above; `chart_node` calls the *same* chart generator functions the 3 chips use for free-form questions.
8. **Real frontend** — login, dashboard, inspect, and chat pages (chatbox at the bottom, the 3 chips above it) replace the current placeholder page in `frontend/`.
9. **Deployment** — containerized services on a host that supports the full Compose stack, direct backend/frontend ports closed so Nginx is the sole entrypoint; a static frontend build can go on Vercel separately, but ClickHouse/ChromaDB/the backend need a real container host (Vercel doesn't run long-lived stateful containers).
