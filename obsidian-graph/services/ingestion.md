# ingestion

**Status**: built — `elt-pipeline-py-script/deploy_elt.py`, run manually on the host (not containerized on purpose, so it's editable/re-runnable with no image in the loop). Not scheduled yet.

Stages, in order, each a plain function that only reads/writes ClickHouse (no in-memory hand-off between stages - deliberate, so each one can become an independent Airflow task later):

1. **Extract** — [[thesportsdb]] (real). Dumps raw JSON into [[clickhouse]]'s `raw_data_store`, untouched.
2. **Transform** — reads the latest raw dump per team/entity back out of `raw_data_store`, parses it into `players`/`clubs`/`matches` rows, plus a hand-curated real `trophies` fixture. Writes into `squad_data_store` (master).
3. **Mock-generate** — [[api-football]] (needs a paid key we don't have yet), and fields with no free source at all ([[access-control]]'s private fields: injuries/salaries/training_load, plus formations) get deterministic synthetic values seeded by the *real* `player_id`s from step 2.
4. **Partition** — fans `squad_data_store` out into the 7 per-team DBs, truncate-and-reload.

Not yet wired up: [[transfermarkt]], [[newsapi-rss]], and a schedule. The long-term plan is an Airflow DAG wrapping these same stages, so re-fetching happens automatically instead of by re-running `deploy_elt.py` by hand - including renewing data once real API keys exist, without needing to babysit the refresh.

← back to [[index]]
