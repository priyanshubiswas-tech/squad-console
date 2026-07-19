# ingestion

The ELT pipeline that fills ClickHouse: `elt-pipeline-py-script/`. Runs on the **host**, deliberately outside Docker, so you can edit any stage and re-run immediately with no image/container in the loop. It talks to ClickHouse through the port `docker-compose.yml` already publishes to `localhost` (`8123`) — never through the in-network hostname `clickhouse` that the backend/frontend containers use.

## Pipeline shape

```
Extract (Wikipedia + TheSportsDB, real)  ->  raw_data_store           [fetchers/]
Transform (real fields)                  ->  squad_data_store (master) [transform/]
Mock-generate (synthetic,
  keyed to real player_ids)              ->  squad_data_store (master) [mock_generators/]
Partition                                ->  the 8 per-team databases  [partition.py]
```

Every stage is a plain Python function that only reads/writes ClickHouse — no stage hands the next one data in memory. That's deliberate groundwork for the **Airflow** layer (`../airflow/`, now built): each function above is one task/operator in the `squad_console_elt` DAG, wired up with a schedule so re-fetching real data (and eventually renewing it as free/paid API keys allow) happens automatically instead of by re-running this script by hand. See the root README's [Scheduled ingestion with Airflow](../README.md#scheduled-ingestion-with-airflow).

## What's real vs. synthetic

| Table | Source | Notes |
|---|---|---|
| `players` | **Real** — Wikipedia (2026 FIFA World Cup squads), photos backfilled from TheSportsDB | Full, real 26-man squads: name, position, club, age. Wikipedia's article is the primary source since TheSportsDB's own national-team profiles only have ~9-10 currently-tagged players each - real, but not a full squad. `overall_rating` is the one synthetic field on this table — no free (or paid) source publishes a FIFA-style rating for real players. `player_id` is a stable hash of the player's name (Wikipedia gives no numeric id); `source` records provenance per row. |
| `clubs` | **Real** — derived from the loaded players | distinct `(club, team_code)` pairs read back from `squad_data_store.players`. `club_id` is a stable hash of the club name (no numeric id available). `league` is blank; resolving it needs one extra API call per club, out of scope for this pass. |
| `matches` | **Real** — TheSportsDB | actual results, including live tournament fixtures. |
| `trophies` | **Real**, hand-curated | TheSportsDB's honours endpoint returns nothing for these teams; `fixtures/trophies.json` is a short, factual list of major titles, checked by hand instead of fetched. |
| `public_stats` | Synthetic | needs a paid API-Football key; deterministic (seeded by real `player_id`) until that key exists. |
| `injuries`, `salaries`, `training_load` | Synthetic | never had a free source, by design — see the build spec. |
| `formations` | Synthetic, but grounded in real data | tactical shapes are authored, but the lineups are built from real players grouped by their real `position` and ranked by the synthetic `overall_rating`. |

This is also the app's actual value proposition, not just a data-quality note — see the root README's "The product: public vs. private data" section. Every synthetic table here doubles as a "private, staff-only" table in the access-control matrix.

## Running it

```bash
cd ingestion/elt-pipeline-py-script
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python deploy_elt.py
```

Requires the `clickhouse` container to be up (`docker compose up -d clickhouse` from the repo root) and reachable on `localhost:8123`. Every run is a full truncate-and-reload — safe to re-run any time, e.g. after editing a mock generator or when TheSportsDB's data changes.

`config.py`'s `CLICKHOUSE_HOST` reads `INGESTION_CLICKHOUSE_HOST` (default `localhost`) rather than the shared `CLICKHOUSE_HOST` the root `.env` sets for the backend (`clickhouse`) — deliberately a separate variable, so a plain host run here never picks up the in-network hostname via `load_dotenv` and points itself at something it can't resolve. The `airflow` container is the one place that *does* set `INGESTION_CLICKHOUSE_HOST=clickhouse`, since it runs this same code in-network (see `docker-compose.yml`).

## Raw landing zone

`raw_data_store.thesportsdb_dumps` (schema in `../database/clickhouse/init/08_raw_data_store.sql`) holds every API response byte-for-byte, timestamped, before any parsing happens — despite the table name, both fetchers write here (`entity` is `team`/`squad`/`matches` for TheSportsDB, `wikipedia_squad` for Wikipedia). Transform stages read the *latest* dump per team/entity from there — never from what the fetch stage returned in memory — so fetch and transform stay decoupled. It's append-only (never truncated), so it also doubles as an audit trail: if a transform script has a bug, you can fix it and re-run against exactly what the API returned, without re-fetching.

## Airflow

Built — `../airflow/dags/squad_elt_dag.py` runs these exact stages as the `squad_console_elt` DAG (extract → transform → mock-generate → partition), scheduled `@daily` with retries, instead of anyone re-triggering `deploy_elt.py` by hand. See the root README's [Scheduled ingestion with Airflow](../README.md#scheduled-ingestion-with-airflow) for how to unpause/trigger it and why it currently sits paused (TheSportsDB's free-tier key rate-limits under real load).
