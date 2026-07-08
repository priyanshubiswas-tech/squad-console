"""Transform stage: raw squad JSON -> squad_data_store.players rows.

Every field here is real except overall_rating, which has no free source
anywhere (not even paid ones - it's a video-game-style rating, not a
football statistic) so it's a deterministic synthetic value seeded by the
player's own real id, kept alongside the real fields rather than pushed
into a separate mock stage.
"""
import json
from datetime import date
from random import Random

from config import TEAMS
from db import get_latest_raw
from transform.shared import real_squad_entries


def _calc_age(date_born: str) -> int:
    if not date_born:
        return 0
    try:
        year, month, day = (int(part) for part in date_born.split("-"))
    except ValueError:
        return 0
    born = date(year, month, day)
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def parse_squad(team_code: str, payload: str) -> list:
    entries = real_squad_entries(json.loads(payload).get("player") or [])
    rows = []
    for entry in entries:
        player_id = int(entry["idPlayer"])
        rng = Random(player_id)
        rows.append({
            "player_id": player_id,
            "name": entry.get("strPlayer") or "",
            "position": entry.get("strPosition") or "",
            "club": entry.get("strTeam") or "",
            "age": _calc_age(entry.get("dateBorn")),
            "overall_rating": rng.randint(60, 90),
            "nationality": entry.get("strNationality") or "",
            "photo_url": entry.get("strThumb") or "",
            "team_code": team_code,
        })
    return rows


def transform_all(client) -> list:
    all_rows = []
    for team_code in TEAMS:
        payload = get_latest_raw(client, team_code, "squad")
        rows = parse_squad(team_code, payload)
        print(f"  {team_code}: {len(rows)} real players")
        all_rows.extend(rows)
    return all_rows
