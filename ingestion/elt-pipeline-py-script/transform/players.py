"""Transform stage: raw squad data -> squad_data_store.players rows.

Wikipedia's squad-list wikitext is the primary source (full, real 26-man
squads). TheSportsDB's squad dump - already fetched for `matches` - is
reused here only to backfill real photo URLs by name match, since Wikipedia
doesn't carry player images in this table.

`source` records where each row's real fields came from, so the app can be
honest in the UI about what's verified vs generated - see
`GET /api/data-sources` on the backend. overall_rating is always synthetic:
no free (or paid) source publishes a FIFA-style rating for real players.
"""
import json
import re
from random import Random

from config import TEAMS
from db import get_latest_raw
from transform.shared import calc_age, real_squad_entries, split_top_level, wikilink_display

POSITION_LABELS = {"GK": "Goalkeeper", "DF": "Defender", "MF": "Midfielder", "FW": "Forward"}

DISPLAY_NAME = {
    "england": "England", "france": "France", "brazil": "Brazil", "argentina": "Argentina",
    "spain": "Spain", "germany": "Germany", "portugal": "Portugal",
}

PLAYER_TEMPLATE_RE = re.compile(r"\{\{nat fs g player\|(.+?)\}\}\n")
AGE_TEMPLATE_RE = re.compile(r"birth date and age2\|df=y\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)")


def _stable_id(name: str) -> int:
    """Deterministic id for players with no numeric id of their own -
    zlib.crc32 always fits UInt32 exactly (0..2**32-1)."""
    import zlib
    return zlib.crc32(name.encode("utf-8"))


def _photo_lookup(squad_payload: str) -> dict:
    """name -> real photo URL, from TheSportsDB's (partial) squad dump."""
    entries = real_squad_entries(json.loads(squad_payload).get("player") or [])
    return {e["strPlayer"].strip().lower(): e.get("strThumb") or "" for e in entries if e.get("strPlayer")}


def parse_wikipedia_squad(team_code: str, wikitext: str, photo_by_name: dict) -> list:
    rows = []
    for raw in PLAYER_TEMPLATE_RE.findall(wikitext):
        fields = {}
        for part in split_top_level(raw):
            if "=" in part:
                key, value = part.split("=", 1)
                fields[key.strip()] = value.strip()

        name = wikilink_display(fields.get("name", ""))
        if not name:
            continue
        club = wikilink_display(fields.get("club", ""))
        position = POSITION_LABELS.get(fields.get("pos", ""), fields.get("pos", ""))

        age_match = AGE_TEMPLATE_RE.search(fields.get("age", ""))
        age = calc_age(int(age_match.group(4)), int(age_match.group(5)), int(age_match.group(6))) if age_match else 0

        player_id = _stable_id(name)
        rng = Random(player_id)
        rows.append({
            "player_id": player_id,
            "name": name,
            "position": position,
            "club": club,
            "age": age,
            "overall_rating": rng.randint(60, 90),
            "nationality": DISPLAY_NAME[team_code],
            "photo_url": photo_by_name.get(name.strip().lower(), ""),
            "team_code": team_code,
            "source": "real:wikipedia",
        })
    return rows


def transform_all(client) -> list:
    all_rows = []
    for team_code in TEAMS:
        wikitext = get_latest_raw(client, team_code, "wikipedia_squad")
        squad_payload = get_latest_raw(client, team_code, "squad")
        photo_by_name = _photo_lookup(squad_payload)

        rows = parse_wikipedia_squad(team_code, wikitext, photo_by_name)
        with_photo = sum(1 for r in rows if r["photo_url"])
        print(f"  {team_code}: {len(rows)} real players ({with_photo} with a real photo)")
        all_rows.extend(rows)
    return all_rows
