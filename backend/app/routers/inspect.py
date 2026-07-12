from fastapi import APIRouter, Depends, HTTPException

from app.access_control import BLOCKED, allowed_columns, get_allowed_tables
from app.config import get_settings
from app.db.clickhouse_client import get_client
from app.deps import get_active_team, require_api_key

router = APIRouter(prefix="/api/inspect", tags=["inspect"], dependencies=[Depends(require_api_key)])


@router.get("/{team_code}")
def inspect_team(team_code: str, active_team: str = Depends(get_active_team)) -> dict:
    team_code = team_code.lower()
    settings = get_settings()
    if team_code not in settings.team_list:
        raise HTTPException(status_code=404, detail=f"Unknown team '{team_code}'")

    allowed = get_allowed_tables(team_code, active_team)
    client = get_client()
    data = {}
    for table, access in allowed.items():
        if access == BLOCKED:
            # Present-but-null, never omitted - the frontend needs the key
            # to render a blur placeholder instead of treating it as absent.
            data[table] = None
            continue
        columns = allowed_columns(table, access)
        select_cols = ", ".join(columns) if columns else "*"
        result = client.query(f"SELECT {select_cols} FROM {team_code}.{table}")
        data[table] = [dict(zip(result.column_names, row)) for row in result.result_rows]
    return data
