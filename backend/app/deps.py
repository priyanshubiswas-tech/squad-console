from typing import Optional

from fastapi import Cookie, HTTPException


def get_active_team(x_active_team: Optional[str] = Cookie(default=None, alias="X-Active-Team")) -> str:
    if not x_active_team:
        raise HTTPException(
            status_code=401,
            detail="No active team selected - call POST /api/session/select-team first",
        )
    return x_active_team
