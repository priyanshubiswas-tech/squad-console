from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from app.config import get_settings
from app.deps import require_api_key

router = APIRouter(prefix="/api/session", tags=["session"], dependencies=[Depends(require_api_key)])


class SelectTeamRequest(BaseModel):
    team_code: str


@router.post("/select-team")
def select_team(payload: SelectTeamRequest, response: Response) -> dict:
    settings = get_settings()
    team_code = payload.team_code.lower()
    if team_code not in settings.team_list:
        raise HTTPException(status_code=404, detail=f"Unknown team '{team_code}'")

    response.set_cookie(key="X-Active-Team", value=team_code, httponly=True, samesite="lax")
    return {"team_code": team_code, "manager_name": settings.managers.get(team_code, "")}
