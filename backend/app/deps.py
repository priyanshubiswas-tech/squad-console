from typing import Optional

from fastapi import Cookie, Header, HTTPException

from app.config import get_settings


def get_active_team(x_active_team: Optional[str] = Cookie(default=None, alias="X-Active-Team")) -> str:
    if not x_active_team:
        raise HTTPException(
            status_code=401,
            detail="No active team selected - call POST /api/session/select-team first",
        )
    # Belt-and-braces: select-team only ever sets this cookie to a value from
    # team_list, but it's httpOnly (not JS-tamperable) rather than signed, so
    # a raw HTTP client or manually-edited cookie could still hand us garbage.
    # Every endpoint that builds SQL by interpolating this value as a
    # database name (team-per-tenant, not a tenant_id column) depends on this
    # check - never build that SQL from an unvalidated team code.
    if x_active_team not in get_settings().team_list:
        raise HTTPException(status_code=400, detail=f"Unknown team '{x_active_team}'")
    return x_active_team


def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> None:
    """Defense in depth: Nginx checks this same shared secret in front of
    everything, but the backend re-checks it independently so the gate
    still means something if this port is ever reached directly."""
    if not x_api_key or x_api_key != get_settings().api_key:
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key")
