import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.charts.generators import injury_risk_chart, top_performers_chart
from app.config import get_settings
from app.deps import get_active_team

router = APIRouter(prefix="/api/charts", tags=["charts"])


@router.get("/{team_code}/injury-risk")
def get_injury_risk_chart(team_code: str, active_team: str = Depends(get_active_team)) -> dict:
    team_code = team_code.lower()
    if team_code != active_team:
        raise HTTPException(status_code=403, detail="training_load is private - can only chart your own team")
    filename = injury_risk_chart(team_code)
    return {"chart_url": f"/api/charts/file/{filename}"}


@router.get("/{team_code}/top-performers")
def get_top_performers_chart(team_code: str, active_team: str = Depends(get_active_team)) -> dict:
    filename = top_performers_chart(team_code.lower())
    return {"chart_url": f"/api/charts/file/{filename}"}


@router.get("/file/{filename}")
def get_chart_file(filename: str):
    settings = get_settings()
    safe_name = os.path.basename(filename)  # no path traversal via ../
    path = os.path.join(settings.chart_output_dir, safe_name)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Chart not found - generate it first")
    return FileResponse(path, media_type="image/png")
