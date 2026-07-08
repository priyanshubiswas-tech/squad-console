# ClickHouse schema

## Layout

- **`squad_data_store`** — master database. Every row from every team lives here, `PARTITION BY team_code`, `ORDER BY (team_code, <primary key>)`. Every table (not just `players`) carries a `team_code` column here, purely so the fan-out step can do a flat `WHERE team_code = '{code}'` per table.
- **`england` / `france` / `brazil` / `argentina` / `spain` / `germany` / `portugal`** — one database per team, identical table shapes to the master minus `team_code` (except `players`, which keeps it) and minus partitioning, since each DB is already scoped to one team.
- **`raw_data_store`** — append-only landing zone for raw API responses, byte-for-byte, before any parsing. See `init/08_raw_data_store.sql` and `../../ingestion/README.md`.

Tables in every team/master database: `players`, `public_stats`, `injuries` (private), `salaries` (private), `training_load` (private), `formations`, `clubs`, `trophies`, `matches`. See `../../architecture/ARCHITECTURE.md` for which fields are "private" and why.

## How the schema gets created

The official `clickhouse/clickhouse-server` image runs every `*.sql` file under `/docker-entrypoint-initdb.d/` **once**, the first time its data directory is empty. `docker-compose.yml` bind-mounts this `init/` folder there, so `docker compose up` self-creates the schema on first boot and never touches it again on subsequent starts — that's what makes `docker compose stop && docker compose start` safe.

If you ever need to force a re-run (e.g. you changed a `.sql` file), you must wipe the ClickHouse volume first: `docker compose down -v` then `docker compose up -d`. This **deletes all data** — only do it in development.

## Populating data

Done by `ingestion/elt-pipeline-py-script/deploy_elt.py`, run from the host (see `../../ingestion/README.md`). It fetches real data from TheSportsDB into `raw_data_store`, transforms it into `squad_data_store.*`, generates the fields that have no free source (keyed to the real `player_id`s), then fans everything into the per-team DBs with a truncate-and-reload pattern:

```sql
INSERT INTO {team}.{table} SELECT * FROM squad_data_store.{table} WHERE team_code = '{code}'
```

Every run replaces all data — safe to re-run any time.

## SOPs

Connect with the CLI client (container must be running):

```bash
docker compose exec clickhouse clickhouse-client --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD"
```

Check the schema landed:

```sql
SHOW DATABASES;                          -- squad_data_store, raw_data_store, england, france, brazil, argentina, spain, germany, portugal
SHOW TABLES FROM squad_data_store;
SHOW TABLES FROM england;
SELECT count() FROM england.players;     -- 0 until ingestion has been run once
```

Or via HTTP from the host (port 8123):

```bash
curl "http://localhost:8123/?query=SHOW+DATABASES" --user "$CLICKHOUSE_USER:$CLICKHOUSE_PASSWORD"
```
