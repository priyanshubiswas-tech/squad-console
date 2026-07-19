"""Extract stage: pull raw JSON from TheSportsDB and land it, untouched, in
raw_data_store. This module never writes to squad_data_store directly - that
separation is what lets a future Airflow DAG run "fetch" and "transform" as
independent tasks that only communicate through the raw table, not shared
process memory.
"""
import time
from datetime import datetime, timezone

import requests

from config import TEAMS, THESPORTSDB_KEY
from transform.shared import DISPLAY_NAME

BASE_URL = f"https://www.thesportsdb.com/api/v1/json/{THESPORTSDB_KEY}"


def resolve_team_id(team_name: str) -> str:
    """Find TheSportsDB's numeric id for a national team by name.

    The free search endpoint returns every sport/club matching the name
    (e.g. searching "Spain" can return futsal/women's/youth entries too), so
    we filter down to the senior men's national side specifically.
    """
    resp = requests.get(f"{BASE_URL}/searchteams.php", params={"t": team_name}, timeout=15)
    resp.raise_for_status()
    candidates = resp.json().get("teams") or []
    for team in candidates:
        if (
            team.get("strSport") == "Soccer"
            and team.get("strGender") == "Male"
            and "FIFA World Cup" in (team.get("strLeague") or "")
        ):
            return team["idTeam"]
    raise RuntimeError(f"Could not resolve a unique national team id for {team_name!r}: {candidates}")


def dump_raw(client, team_code: str, entity: str, source_url: str, payload_text: str) -> None:
    client.insert(
        "raw_data_store.thesportsdb_dumps",
        [[datetime.now(timezone.utc), team_code, entity, source_url, payload_text]],
        column_names=["fetched_at", "team_code", "entity", "source_url", "payload"],
    )


def fetch_and_dump_team(client, team_code: str) -> None:
    team_id = resolve_team_id(DISPLAY_NAME[team_code])

    calls = [
        ("team", f"{BASE_URL}/lookupteam.php?id={team_id}"),
        ("squad", f"{BASE_URL}/lookup_all_players.php?id={team_id}"),
        ("matches", f"{BASE_URL}/eventslast.php?id={team_id}"),
    ]
    for entity, url in calls:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        dump_raw(client, team_code, entity, url, resp.text)
        print(f"  fetched {team_code}/{entity} ({len(resp.text)} bytes) <- {url}")


def fetch_all(client) -> None:
    print(f"Extract: TheSportsDB, {len(TEAMS)} teams")
    for team_code in TEAMS:
        fetch_and_dump_team(client, team_code)
        time.sleep(1)  # polite pacing, well under the free tier's rate limit
