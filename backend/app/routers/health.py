from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.db.clickhouse_client import get_client

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def health() -> dict:
    return {"status": "ok"}


@router.get("/clickhouse")
def clickhouse_health() -> dict:
    settings = get_settings()
    client = get_client()
    try:
        client.query("SELECT 1")
        databases = [row[0] for row in client.query("SHOW DATABASES").result_rows]
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"ClickHouse unreachable: {exc}") from exc

    expected = {settings.clickhouse_master_db, *settings.team_list}
    missing = sorted(expected - set(databases))

    return {
        "status": "ok" if not missing else "schema incomplete",
        "databases": sorted(databases),
        "missing": missing,
    }
