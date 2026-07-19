import os
from pathlib import Path

from dotenv import load_dotenv

# These scripts run on the host by default, deliberately outside Docker, so
# you can edit and re-run them with no image/container in the loop at all.
# They reach ClickHouse through the port docker-compose already publishes to
# localhost - never through the in-network hostname "clickhouse" that the
# backend/frontend containers use (that name only resolves inside squadnet).
# The Airflow container is the one exception: it runs these same modules
# in-network, so it sets INGESTION_CLICKHOUSE_HOST=clickhouse in its own
# environment (see docker-compose.yml) - deliberately a *different* variable
# from the shared CLICKHOUSE_HOST the root .env sets for backend/frontend,
# so a plain host run of this pipeline never silently picks that up via
# load_dotenv below and points itself at a hostname it can't resolve.
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

CLICKHOUSE_HOST = os.environ.get("INGESTION_CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.environ.get("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "changeme")
CLICKHOUSE_MASTER_DB = os.environ.get("CLICKHOUSE_MASTER_DB", "squad_data_store")

TEAMS = [t.strip() for t in os.environ.get(
    "TEAMS", "england,france,brazil,argentina,spain,germany,portugal,capeverde"
).split(",") if t.strip()]

THESPORTSDB_KEY = os.environ.get("THESPORTSDB_KEY", "3")
