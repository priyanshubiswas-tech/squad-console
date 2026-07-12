from typing import Optional

from fastapi import Cookie, Header, HTTPException

from app.config import get_settings


def get_active_team(x_active_team: Optional[str] = Cookie(default=None, alias="X-Active-Team")) -> str:
    if not x_active_team:
        raise HTTPException(
            status_code=401,
            detail="No active team selected - call POST /api/session/select-team first",
        )
    return x_active_team


def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> None:
    """Defense in depth: Nginx checks this same shared secret in front of
    everything, but the backend re-checks it independently so the gate
    still means something if this port is ever reached directly."""
    if not x_api_key or x_api_key != get_settings().api_key:
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key")
