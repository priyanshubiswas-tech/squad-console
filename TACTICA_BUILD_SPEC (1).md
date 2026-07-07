# Tactica — FIFA World Cup Manager Console
## Build Specification for AI Coding Agents (Claude Code / Cursor / Windsurf / etc.)

> **How to use this file**: Feed this entire document to your AI coding agent as the project spec. Build in the phase order given — each phase produces a working, demoable increment. Do not skip ahead to "real APIs" (Phase 8) until Phases 1-7 work end-to-end on mock data.

---

## 1. Project summary

A web app where a national-team manager (England, Brazil, Argentina, France, Germany, Spain, Portugal — **only these 7 teams**) logs in by selecting their federation crest (no typing), and gets:

- A **dashboard** of their own squad: players, ratings, injuries, salaries, training load, formations, top performers.
- An **"Inspect other squads"** view: same dashboard layout for any of the other 6 teams, but with `injuries`, `salaries`, and `training_load` fields **redacted/blurred** — only public stats, basic player info, clubs and trophies are visible.
- A **chatbot ("Ask the analyst")** built with LangGraph + RAG that answers tactical questions ("What formation should I use vs Brazil and why?") using the active team's full data + the opponent's public data only, and can return charts (matplotlib/seaborn PNGs).
- A **team switcher** in the top-right (with manager avatar) that triggers a full page reload and changes the active `team_context` everywhere.

---

## 2. Tech stack

| Layer | Tech |
|---|---|
| Frontend | React + Tailwind CSS, dark gradient football theme |
| Reverse proxy | Nginx |
| Backend | FastAPI (Python) |
| Agent orchestration | LangGraph |
| Vector store | ChromaDB |
| Analytical DB | ClickHouse |
| Scheduling/ingestion | Python + APScheduler (NOT Airflow for v1 — see §9) |
| Charts | matplotlib / seaborn (rendered server-side to PNG) |
| Containerization | Docker + docker-compose, named volumes for persistence |
| Config | `.env` file, all secrets/keys as placeholders until Phase 8 |

---

## 3. Environment variables (`.env`)

Create this file at the repo root from day one. All code reads from it — never hardcode values.

```bash
# --- ClickHouse ---
CLICKHOUSE_HOST=clickhouse
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=changeme
CLICKHOUSE_MASTER_DB=fifa_data_store

# --- ChromaDB ---
CHROMA_HOST=chroma
CHROMA_PORT=8000

# --- LLM provider (used by LangGraph reasoning node) ---
LLM_PROVIDER=anthropic            # or openai
ANTHROPIC_API_KEY=                # fill in later
OPENAI_API_KEY=                   # fill in later
LLM_MODEL=claude-sonnet-4-6

# --- External data APIs (Phase 8 — leave blank for now) ---
API_FOOTBALL_KEY=
THESPORTSDB_KEY=3                 # "3" is the public test key
NEWSAPI_KEY=
TRANSFERMARKT_API_BASE=http://transfermarkt-api:8000

# --- App config ---
TEAMS=england,france,brazil,argentina,spain,germany,portugal
INGESTION_INTERVAL_HOURS=6
CHART_OUTPUT_DIR=/app/charts

# --- Manager identity mapping (used by login page, no auth/passwords) ---
MANAGER_ENGLAND="Thomas Tuchel"
MANAGER_FRANCE="Didier Deschamps"
MANAGER_BRAZIL="Carlo Ancelotti"
MANAGER_ARGENTINA="Lionel Scaloni"
MANAGER_SPAIN="Luis de la Fuente"
MANAGER_GERMANY="Julian Nagelsmann"
MANAGER_PORTUGAL="Roberto Martinez"
```

---

## 4. Repo structure

```
fifa-manager/
├── docker-compose.yml
├── .env
├── .env.example
├── nginx/
│   └── nginx.conf
├── ingestion/
│   ├── fetchers/
│   │   ├── api_football.py
│   │   ├── sportsdb.py
│   │   ├── transfermarkt.py
│   │   └── rss_news.py
│   ├── mock_generators/
│   │   ├── generate_players.py
│   │   ├── generate_injuries.py
│   │   ├── generate_salaries.py
│   │   ├── generate_training_load.py
│   │   ├── generate_formations.py
│   │   └── generate_tactics_notes.py
│   ├── partition.py
│   ├── scheduler.py
│   ├── requirements.txt
│   └── Dockerfile
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── auth.py
│   │   ├── access_control.py
│   │   ├── routers/
│   │   │   ├── session.py
│   │   │   ├── dashboard.py
│   │   │   ├── inspect.py
│   │   │   ├── news.py
│   │   │   └── chat.py
│   │   ├── db/
│   │   │   ├── clickhouse_client.py
│   │   │   └── chroma_client.py
│   │   ├── langgraph_app/
│   │   │   ├── graph.py
│   │   │   ├── state.py
│   │   │   ├── nodes/
│   │   │   │   ├── intent_router.py
│   │   │   │   ├── stats_tool.py
│   │   │   │   ├── rag_retriever.py
│   │   │   │   ├── access_filter.py
│   │   │   │   ├── reasoner.py
│   │   │   │   ├── chart_node.py
│   │   │   │   └── composer.py
│   │   │   └── prompts/
│   │   │       └── reasoner_prompt.txt
│   │   └── charts/            # mounted volume, generated PNGs
│   ├── requirements.txt
│   └── Dockerfile
├── embedding_job/
│   ├── embed_team_docs.py
│   ├── requirements.txt
│   └── Dockerfile
├── knowledge_base/
│   ├── england/{tactics_notes.md, public_scouting.md, news/}
│   ├── france/...
│   ├── brazil/...
│   ├── argentina/...
│   ├── spain/...
│   ├── germany/...
│   ├── portugal/...
│   └── shared/tactical_theory.md
└── frontend/
    ├── src/
    │   ├── pages/{Login.tsx, Dashboard.tsx, InspectSquad.tsx, Tactics.tsx, News.tsx}
    │   ├── components/{Header.tsx, TeamSelector.tsx, ChatPanel.tsx, FormationCard.tsx,
    │   │                SquadTable.tsx, BlurredField.tsx, MetricCard.tsx, Sidebar.tsx}
    │   ├── context/TeamContext.tsx
    │   └── api/client.ts
    ├── tailwind.config.js
    ├── package.json
    └── Dockerfile
```

---

## 5. Phase-by-phase build order

### Phase 1 — Mock data generators
Build `ingestion/mock_generators/*.py`. Each script outputs JSON for all 7 teams, ~20-26 players each, with realistic but fictional values:
- `players`: player_id, name, position, club, age, overall_rating, nationality, photo_url (use TheSportsDB or placeholder image URLs), team_code
- `public_stats`: goals, assists, key_passes, tackles, rating_avg, matches_played
- `injuries`: 2-4 per team, injury_type, status, expected_return, severity
- `salaries`: weekly_wage, contract_until
- `training_load`: per player, weekly load_score + fatigue_index for 4 weeks
- `formations`: 3 formations per team (e.g. 4-3-3, 4-2-3-1, 3-5-2), players_json mapping, notes, suitable_vs
- `clubs`, `trophies`, `matches`: basic fictional/real-ish data

Also write `knowledge_base/{team}/tactics_notes.md` and `public_scouting.md` for each team — 200-400 words of tactical narrative per team (you write this content; it becomes the RAG corpus and directly drives chatbot answer quality). Include player-specific tactical notes (e.g. "Vinícius Jr's pace on the left favours teams that overload the right side defensively").

**Acceptance**: running `python ingestion/mock_generators/run_all.py` produces JSON files for all 7 teams + markdown files in `knowledge_base/`.

### Phase 2 — ClickHouse schema + partitioning
1. Write DDL (see §6) to create `fifa_data_store` (partitioned by `team_code`) and 7 per-team databases with identical table structures.
2. Write `ingestion/partition.py`: reads mock JSON → inserts into `fifa_data_store.*` → fans out into per-team DBs via `INSERT INTO {team}.{table} SELECT * FROM fifa_data_store.{table} WHERE team_code = '{code}'` (truncate-and-reload pattern for v1).
3. Run it, verify with `clickhouse-client` that `england.players` has England's 26 players and `fifa_data_store.players` has all 7 teams.

**Acceptance**: `SELECT count() FROM england.players` = 26 (or your chosen squad size); `SELECT count() FROM fifa_data_store.players` = 7 × squad size.

### Phase 3 — FastAPI backend skeleton + access control
1. `backend/app/access_control.py`: implement `get_allowed_tables(requested_team, active_team) -> dict` exactly per the matrix in §7.
2. `backend/app/routers/session.py`: `POST /api/session/select-team` — sets `X-Active-Team` as an httpOnly cookie, returns `{team_code, manager_name}` from `.env` mapping.
3. `backend/app/routers/dashboard.py`: `GET /api/dashboard/{team_code}` — 403 if `team_code != active_team` (cookie). Returns full JSON: players + public_stats + injuries + salaries + training_load + formations + clubs + trophies.
4. `backend/app/routers/inspect.py`: `GET /api/inspect/{team_code}` — runs `get_allowed_tables(team_code, active_team)`; for "blocked" tables, returns `null` for those fields (do **not** omit the keys — frontend needs them present-but-null to render the blur placeholder); for "partial" (formations), strips `players_json` and `notes`.

**Acceptance**: with cookie `X-Active-Team=england`, `GET /api/dashboard/england` returns full data; `GET /api/inspect/brazil` returns `injuries: null`, `salaries: null`, `training_load: null`, and `formations` entries with only `name`/`suitable_vs`.

### Phase 4 — Frontend: login, dashboard, inspect, team switcher
1. `Login.tsx`: grid of 7 crests (static images or initials avatars), each showing the manager name from a small static config (mirrors `.env` mapping — duplicate it in a `frontend/src/config/managers.ts` for simplicity). Clicking → `POST /api/session/select-team` → redirect to `/dashboard`.
2. `Header.tsx`: team-select dropdown (top right) + manager avatar/name. On change → call select-team endpoint → `window.location.reload()`.
3. `Dashboard.tsx`: metric cards (squad size, available, injured, avg rating), formation cards (highlight recommended), top performers grid, injury list, squad table.
4. `InspectSquad.tsx`: team picker for the other 6 teams, renders same layout components but with `<BlurredField/>` wherever a value is `null` — show a lock icon + "Private to {team} staff".
5. Apply the dark gradient football theme per §10 (Design system).

**Acceptance**: Can log in as any of 7 teams, see own full dashboard, switch to "inspect" any other team and see blurred private fields, switch active team via header and have the whole UI reload with new context.

### Phase 5 — ChromaDB + embedding job
1. `embedding_job/embed_team_docs.py`: for each team, chunk and embed `knowledge_base/{team}/tactics_notes.md` into collection `{team}_full`, and `public_scouting.md` into `{team}_public`. Embed `knowledge_base/shared/tactical_theory.md` into `shared_theory`. Attach metadata `{team, doc_type, visibility}` to every chunk.
2. Run as a one-off job (and re-run whenever `knowledge_base/` changes — wire into the scheduler in Phase 9).

**Acceptance**: `chroma_client.get_collection("england_full").count() > 0` and similarly for all teams + `shared_theory`.

### Phase 6 — LangGraph agent
Implement each node in `backend/app/langgraph_app/nodes/` per the spec in §8, wire the graph in `graph.py`, expose via `backend/app/routers/chat.py`: `POST /api/chat {message, active_team}`.

Test prompts to validate:
- "What formation should I use against Brazil and why?" → should retrieve `england_full` + `brazil_public` + `shared_theory`, return formation recommendation referencing specific opponent players from the public scouting doc.
- "Who are my top scorers?" → stats-only path, no RAG needed, no chart.
- "Compare my midfield to Brazil's" → triggers `chart_node`, returns `chart_url`.
- "What's Brazil's injury situation?" → must NOT return injury data (verify `access_filter` blocks it); answer should state that information is private.

**Acceptance**: all 4 test prompts return correct, privacy-respecting answers; chart prompt returns a valid PNG URL.

### Phase 7 — Nginx + docker-compose + persistence
1. `nginx/nginx.conf`: proxy `/api/*` → backend, everything else → frontend static build.
2. `docker-compose.yml` per §9 with named volumes for `clickhouse_data`, `chroma_data`, `charts_data`, and bind-mount for `knowledge_base`.
3. Verify: `docker compose up -d`, use the app, `docker compose stop`, `docker compose start` — all data (ClickHouse tables, Chroma embeddings, generated charts) must still be present. Only `docker compose down -v` should wipe it.

**Acceptance**: full app reachable at `http://localhost`, survives stop/start cycles with data intact.

### Phase 8 — Swap mock data for real APIs (do this LAST)
1. Implement `ingestion/fetchers/*.py` using the free APIs in §11. Each fetcher should output the **same JSON shape** as the Phase 1 mock generators — this is the contract that makes the swap a drop-in.
2. Add real API keys to `.env`.
3. Toggle via `.env` flag `USE_MOCK_DATA=false` in `scheduler.py` — fetchers run instead of mock generators, same `partition.py` pipeline.
4. For fields with no free source (injuries detail, salaries, training_load, tactics) — keep using mock generators even in "real" mode; document this clearly in the README as "synthetic internal data, modeled on real squads."

### Phase 9 — Scheduling
`ingestion/scheduler.py` using APScheduler: runs ingestion + `partition.py` + (if `knowledge_base/` changed) the embedding job, every `INGESTION_INTERVAL_HOURS`. Runs as its own container, restarts with the stack.

*(Optional Phase 10: migrate `scheduler.py` logic into an Airflow DAG if you want it on your resume — only after everything above works.)*

---

## 6. ClickHouse schema (apply to `fifa_data_store` AND each of the 7 per-team DBs)

```sql
CREATE TABLE players (
    player_id UInt32, name String, position String, club String, age UInt8,
    overall_rating UInt8, nationality String, photo_url String, team_code String
) ENGINE = MergeTree() ORDER BY player_id;

CREATE TABLE public_stats (
    player_id UInt32, goals UInt16, assists UInt16, key_passes UInt16,
    tackles UInt16, rating_avg Float32, matches_played UInt16
) ENGINE = MergeTree() ORDER BY player_id;

CREATE TABLE injuries (              -- PRIVATE
    player_id UInt32, injury_type String, status String,
    expected_return Date, severity String
) ENGINE = MergeTree() ORDER BY player_id;

CREATE TABLE salaries (               -- PRIVATE
    player_id UInt32, weekly_wage UInt32, contract_until Date
) ENGINE = MergeTree() ORDER BY player_id;

CREATE TABLE training_load (          -- PRIVATE
    player_id UInt32, week_no UInt8, load_score Float32, fatigue_index Float32
) ENGINE = MergeTree() ORDER BY (player_id, week_no);

CREATE TABLE formations (
    formation_id UInt32, name String, players_json String, notes String, suitable_vs String
) ENGINE = MergeTree() ORDER BY formation_id;

CREATE TABLE clubs    (club_id UInt32, name String, league String) ENGINE = MergeTree() ORDER BY club_id;
CREATE TABLE trophies (trophy_id UInt32, name String, year UInt16) ENGINE = MergeTree() ORDER BY trophy_id;
CREATE TABLE matches  (match_id UInt32, opponent String, date Date, result String,
                       goals_for UInt8, goals_against UInt8) ENGINE = MergeTree() ORDER BY match_id;
```

For `fifa_data_store`, add `PARTITION BY team_code` to every `ENGINE = MergeTree()` line and change `ORDER BY x` → `ORDER BY (team_code, x)`.

---

## 7. Access control matrix

| Table | `requested_team == active_team` | `requested_team != active_team` (inspect mode) |
|---|---|---|
| `players` (basic fields) | full | full |
| `public_stats` | full | full |
| `clubs`, `trophies`, `matches` | full | full |
| `injuries` | full | **null** (blocked) |
| `salaries` | full | **null** (blocked) |
| `training_load` | full | **null** (blocked) |
| `formations` | full | `name` + `suitable_vs` only |

This logic lives in **one function** (`access_control.get_allowed_tables`) used by both `inspect.py` and the LangGraph `access_filter` node — never duplicate this logic.

---

## 8. LangGraph specification

### State
```python
class AgentState(TypedDict):
    user_query: str
    active_team: str
    opponent_team: Optional[str]
    intent: str  # "tactical_advice" | "stat_lookup" | "comparison" | "general"
    own_stats: dict
    opponent_public_stats: dict
    retrieved_docs: list[str]
    chart_path: Optional[str]
    final_answer: str
```

### Nodes (in order)
1. **intent_router** — LLM or keyword-based classification; extract `opponent_team` from phrases like "vs Brazil".
2. **stats_tool** — ClickHouse: own team's `players` + `public_stats` + `formations` (full); if `opponent_team` set, its `public_stats` only (via `get_allowed_tables`).
3. **rag_retriever** — Chroma: `{active_team}_full` (always) + `{opponent_team}_public` + `shared_theory` (if opponent set).
4. **access_filter** — re-applies `get_allowed_tables` as a final check on `opponent_public_stats` and `retrieved_docs` metadata; drops anything with `visibility != "public"` for non-active teams.
5. **reasoner** — LLM call using `backend/app/langgraph_app/prompts/reasoner_prompt.txt`, given own stats + formations + retrieved docs + opponent public stats/docs → produces structured tactical recommendation text.
6. **chart_node** (conditional, `needs_chart(state)` true if intent == "comparison" or reasoner output references a head-to-head comparison) — generates matplotlib/seaborn chart (bar/radar), saves to `CHART_OUTPUT_DIR`, sets `chart_path`.
7. **composer** — returns `{text: final_answer, chart_url: "/api/charts/{filename}" or null}`.

### Edges
`intent_router → stats_tool → rag_retriever → access_filter → reasoner → [conditional: chart_node | composer] → composer → END`

---

## 9. docker-compose skeleton

```yaml
volumes:
  clickhouse_data:
  chroma_data:
  charts_data:

services:
  clickhouse:
    image: clickhouse/clickhouse-server:latest
    volumes:
      - clickhouse_data:/var/lib/clickhouse
    env_file: .env

  chroma:
    image: chromadb/chroma:latest
    volumes:
      - chroma_data:/chroma/chroma

  ingestion:
    build: ./ingestion
    env_file: .env
    volumes:
      - ./knowledge_base:/app/knowledge_base
    depends_on: [clickhouse]

  embedding_job:
    build: ./embedding_job
    env_file: .env
    volumes:
      - ./knowledge_base:/app/knowledge_base
    depends_on: [chroma]

  backend:
    build: ./backend
    env_file: .env
    volumes:
      - charts_data:/app/charts
    depends_on: [clickhouse, chroma]

  frontend:
    build: ./frontend
    depends_on: [backend]

  nginx:
    image: nginx:alpine
    ports: ["80:80"]
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on: [backend, frontend]
```

**Persistence rule**: `docker compose stop` / `start` / `restart` preserve all volumes. Only `docker compose down -v` removes them. Document this prominently in the README.

---

## 10. Design system (dark football theme)

- Background: `#0a0e14`; Panels: `#121826`; Cards: `#171f30`; Card hover/highlight: `#1c2740`
- Accent 1 (pitch green): `#22c55e` — used for "recommended" highlights, positive stats, available players
- Accent 2 (night indigo): `#6366f1` — used for avatars, header gradient, active nav item
- Danger (injuries): `#ef4444`
- Lock/private indicator: `#facc15` (amber) + lock icon
- Text: primary `#e5e7eb`, secondary `#9ca3af`
- Header: subtle gradient using the active team's two accent colors (see team color list below) blended into the indigo/green base — re-skins on team switch
- Typography: system sans-serif stack, headings 500 weight, body 400
- Cards: `border-radius: 12px`, 1px borders `#2a3344`, no heavy shadows
- Blurred/private fields: `filter: blur(4px)` placeholder bars + amber lock icon + caption "Private to {team} staff" — values are `null` from the API, never sent unmasked

**Per-team header accent pairs** (primary/secondary):
- England: `#1e3a8a` / `#dc2626`
- Brazil: `#facc15` / `#16a34a`
- Argentina: `#60a5fa` / `#ffffff`
- France: `#1e3a8a` / `#dc2626`
- Germany: `#111827` / `#dc2626`
- Spain: `#dc2626` / `#facc15`
- Portugal: `#16a34a` / `#dc2626`

### Pages
1. **Login** — full-bleed dark background, centered heading "Select your federation", grid of 7 crest cards (team name + manager name beneath), no text inputs.
2. **Dashboard** — header (logo, team selector, manager avatar) | left sidebar nav (My squad / Inspect other squads / Tactics & formations / News & trends / Ask the analyst) | main area (4 metric cards, formations row with recommended highlighted, injury list, top performers grid, squad table) | right column persistent chat panel.
3. **Inspect other squads** — same layout as dashboard but: banner stating "Read-only public view — injuries, salaries and training load are hidden", and those three sections render `<BlurredField/>` placeholders.
4. **Tactics & formations** — full formation library for active team with pitch diagrams (SVG) per formation.
5. **News & trends** — RSS-sourced articles for active team, card list.

---

## 11. Free data sources reference

| Need | Source | Notes |
|---|---|---|
| Squads, player profiles, photos | TheSportsDB (free, key `3` for testing) | player images, badges, bios |
| Player stats, fixtures, standings | API-Football (RapidAPI free tier, 100 req/day) | cache aggressively in ClickHouse |
| Fixtures/results | football-data.org free tier | rate-limited |
| Market value / squad depth | transfermarkt-api (self-hosted OSS wrapper) | proxy for "salary" data |
| Player bios, trophies | Wikipedia/Wikidata REST API | free, unlimited |
| Trending news | RSS feeds (BBC Sport, Sky Sports, ESPN) or NewsAPI free tier | RSS preferred for reliability |
| Injuries (partial real coverage) | API-Football injuries endpoint | supplement gaps with mock data |
| Training regimens, tactics, formations, salaries (detail) | **Synthetic — Phase 1 mock generators, never replaced** | this is your RAG knowledge base content |

---

## 12. Definition of done

- [ ] All 7 teams selectable from login, no text input
- [ ] Own dashboard shows full data for all sections
- [ ] Inspect mode shows blurred/locked injuries, salaries, training_load for other teams
- [ ] Team switch in header reloads app with new `X-Active-Team`
- [ ] Chatbot answers tactical questions referencing opponent's public players/tactics correctly
- [ ] Chatbot never leaks opponent private fields (test explicitly)
- [ ] Chatbot can return charts inline
- [ ] `docker compose stop && docker compose start` preserves all data
- [ ] `.env` contains all keys/placeholders; app runs fully on mock data with empty API keys
