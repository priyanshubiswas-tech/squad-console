from fastapi import APIRouter, Depends, HTTPException

from app.config import get_settings
from app.db.clickhouse_client import get_client
from app.deps import get_active_team

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

TABLES = [
    "players", "public_stats", "injuries", "salaries",
    "training_load", "formations", "clubs", "trophies", "matches",
]


@router.get("/{team_code}")
def get_dashboard(team_code: str, active_team: str = Depends(get_active_team)) -> dict:
    team_code = team_code.lower()
    settings = get_settings()
    if team_code not in settings.team_list:
        raise HTTPException(status_code=404, detail=f"Unknown team '{team_code}'")
    if team_code != active_team:
        raise HTTPException(
            status_code=403,
            detail=f"Can only view your own team's full dashboard - use /api/inspect/{team_code} instead",
        )

    client = get_client()
    data = {}
    for table in TABLES:
        result = client.query(f"SELECT * FROM {team_code}.{table}")
        data[table] = [dict(zip(result.column_names, row)) for row in result.result_rows]
    return data
