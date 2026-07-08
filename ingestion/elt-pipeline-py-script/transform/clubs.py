"""Transform stage: raw squad JSON -> squad_data_store.clubs rows.

Clubs are derived from the real squad data (every player's current club and
its real TheSportsDB id), de-duplicated per team. `league` is left blank -
TheSportsDB's squad endpoint doesn't return it, and resolving it would need
one extra API call per distinct club, which is out of scope for this pass.
"""
import json

from config import TEAMS
from db import get_latest_raw
from transform.shared import real_squad_entries


def parse_clubs(team_code: str, payload: str) -> list:
    entries = real_squad_entries(json.loads(payload).get("player") or [])
    seen = {}
    for entry in entries:
        club_id = entry.get("idTeam")
        club_name = entry.get("strTeam")
        if not club_id or not club_name or club_id in seen:
            continue
        seen[club_id] = {
            "club_id": int(club_id),
            "name": club_name,
            "league": "",
            "team_code": team_code,
        }
    return list(seen.values())


def transform_all(client) -> list:
    all_rows = []
    for team_code in TEAMS:
        payload = get_latest_raw(client, team_code, "squad")
        rows = parse_clubs(team_code, payload)
        print(f"  {team_code}: {len(rows)} distinct clubs")
        all_rows.extend(rows)
    return all_rows
