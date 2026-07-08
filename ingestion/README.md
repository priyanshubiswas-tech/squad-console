# ingestion

The ELT pipeline that fills ClickHouse: `elt-pipeline-py-script/`. Runs on the **host**, deliberately outside Docker, so you can edit any stage and re-run immediately with no image/container in the loop. It talks to ClickHouse through the port `docker-compose.yml` already publishes to `localhost` (`8123`) — never through the in-network hostname `clickhouse` that the backend/frontend containers use.

## Pipeline shape

```
Extract (TheSportsDB, real)  ->  raw_data_store               [fetchers/]
Transform (real fields)      ->  squad_data_store (master)     [transform/]
Mock-generate (synthetic,
  keyed to real player_ids)  ->  squad_data_store (master)     [mock_generators/]
Partition                    ->  the 7 per-team databases      [partition.py]
```

Every stage is a plain Python function that only reads/writes ClickHouse — no stage hands the next one data in memory. That's deliberate groundwork for the planned **Airflow** layer: each function below becomes one task/operator later, wired up with a schedule so re-fetching real data (and eventually renewing it as free/paid API keys allow) happens automatically instead of by re-running this script by hand.

## What's real vs. synthetic

| Table | Source | Notes |
|---|---|---|
| `players` | **Real** — TheSportsDB | name, position, club, age, nationality, photo. `overall_rating` is the one synthetic field on this table — no free (or paid) source publishes a FIFA-style rating for real players. |
| `clubs` | **Real** — derived from squad data | `league` is blank; resolving it needs one extra API call per club, out of scope for this pass. |
| `matches` | **Real** — TheSportsDB | actual results, including live tournament fixtures. |
| `trophies` | **Real**, hand-curated | TheSportsDB's honours endpoint returns nothing for these teams; `fixtures/trophies.json` is a short, factual list of major titles, checked by hand instead of fetched. |
| `public_stats` | Synthetic | needs a paid API-Football key; deterministic (seeded by real `player_id`) until that key exists. |
| `injuries`, `salaries`, `training_load` | Synthetic | never had a free source, by design — see the build spec. |
| `formations` | Synthetic, but grounded in real data | tactical shapes are authored, but the lineups are built from real players grouped by their real `position` and ranked by the synthetic `overall_rating`. |

## Running it

```bash
cd ingestion/elt-pipeline-py-script
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python deploy_elt.py
```

Requires the `clickhouse` container to be up (`docker compose up -d clickhouse` from the repo root) and reachable on `localhost:8123`. Every run is a full truncate-and-reload — safe to re-run any time, e.g. after editing a mock generator or when TheSportsDB's data changes.

## Raw landing zone

`raw_data_store.thesportsdb_dumps` (schema in `../database/clickhouse/init/08_raw_data_store.sql`) holds every API response byte-for-byte, timestamped, before any parsing happens. Transform stages read the *latest* dump per team/entity from there — never from what the fetch stage returned in memory — so fetch and transform stay decoupled. It's append-only (never truncated), so it also doubles as an audit trail: if a transform script has a bug, you can fix it and re-run against exactly what the API returned, without re-fetching.

## Next: Airflow

Not built yet. The long-term plan is to move `deploy_elt.py`'s stages into an Airflow DAG so the whole pipeline runs on a schedule with retries/checkups, and so real-time-ish refresh (once real API keys exist) doesn't require anyone to re-trigger it by hand.
