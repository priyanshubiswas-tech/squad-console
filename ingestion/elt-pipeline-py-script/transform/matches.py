"""Transform stage: raw match-events JSON -> squad_data_store.matches rows.

All real: TheSportsDB's eventslast endpoint returns actual results,
including live tournament fixtures.
"""
import json
from datetime import date as date_cls

from config import TEAMS
from db import get_latest_raw


def parse_matches(team_code: str, payload: str) -> list:
    events = json.loads(payload).get("results") or []
    rows = []
    for event in events:
        home_score, away_score = event.get("intHomeScore"), event.get("intAwayScore")
        if home_score is None or away_score is None:
            continue  # not yet played

        is_home = (event.get("strHomeTeam") or "").lower() == team_code.lower()
        goals_for = int(home_score) if is_home else int(away_score)
        goals_against = int(away_score) if is_home else int(home_score)
        opponent = event.get("strAwayTeam") if is_home else event.get("strHomeTeam")
        outcome = "W" if goals_for > goals_against else "D" if goals_for == goals_against else "L"

        try:
            year, month, day = (int(part) for part in (event.get("dateEvent") or "").split("-"))
            match_date = date_cls(year, month, day)
        except ValueError:
            continue

        rows.append({
            "match_id": int(event["idEvent"]),
            "opponent": opponent or "",
            "date": match_date,
            "result": f"{outcome} {goals_for}-{goals_against}",
            "goals_for": goals_for,
            "goals_against": goals_against,
            "team_code": team_code,
        })
    return rows


def transform_all(client) -> list:
    all_rows = []
    for team_code in TEAMS:
        payload = get_latest_raw(client, team_code, "matches")
        rows = parse_matches(team_code, payload)
        print(f"  {team_code}: {len(rows)} matches")
        all_rows.extend(rows)
    return all_rows
