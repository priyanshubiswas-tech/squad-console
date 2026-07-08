import os
from pathlib import Path

from dotenv import load_dotenv

# These scripts run on the host, deliberately outside Docker, so you can
# edit and re-run them with no image/container in the loop at all. They
# reach ClickHouse through the port docker-compose already publishes to
# localhost - never through the in-network hostname "clickhouse" that the
# backend/frontend containers use (that name only resolves inside squadnet).
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = int(os.environ.get("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "changeme")
CLICKHOUSE_MASTER_DB = os.environ.get("CLICKHOUSE_MASTER_DB", "squad_data_store")

TEAMS = [t.strip() for t in os.environ.get(
    "TEAMS", "england,france,brazil,argentina,spain,germany,portugal"
).split(",") if t.strip()]

THESPORTSDB_KEY = os.environ.get("THESPORTSDB_KEY", "3")
