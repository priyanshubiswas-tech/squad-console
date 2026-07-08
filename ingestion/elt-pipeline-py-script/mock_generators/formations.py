"""Tactical formations are our own authoring, not fetched from anywhere -
but grounded in the real squad instead of invented names. Players are
bucketed by their real `position` string and picked by the synthetic
overall_rating already stored on squad_data_store.players.
"""
import json
from random import Random

from config import CLICKHOUSE_MASTER_DB

SHAPES = {
    "4-3-3": {"GK": 1, "DF": 4, "MF": 3, "FW": 3},
    "4-2-3-1": {"GK": 1, "DF": 4, "MF": 5, "FW": 1},
    "4-4-2": {"GK": 1, "DF": 4, "MF": 4, "FW": 2},
}
SUITABLE_VS = {
    "4-3-3": "Balanced - wide forwards stretch teams that sit in a low block",
    "4-2-3-1": "Possession-heavy opponents - extra central midfielder controls tempo",
    "4-4-2": "High-press opponents - two out-and-out strikers punish a high line",
}


def _bucket(position: str) -> str:
    p = position.lower()
    if "keeper" in p:
        return "GK"
    if "back" in p:
        return "DF"
    if "midfield" in p:
        return "MF"
    if "defen" in p:
        return "DF"
    return "FW"


def _build_players_json(players_by_bucket: dict, shape: dict) -> str:
    lineup = {}
    for bucket, count in shape.items():
        candidates = players_by_bucket.get(bucket, [])
        lineup[bucket] = [name for name, _rating in candidates[:count]]
    return json.dumps(lineup)


def generate(client) -> list:
    players = client.query(
        f"SELECT player_id, team_code, position, overall_rating, name FROM {CLICKHOUSE_MASTER_DB}.players"
    ).result_rows

    by_team = {}
    for player_id, team_code, position, overall_rating, name in players:
        by_team.setdefault(team_code, {}).setdefault(_bucket(position), []).append((name, overall_rating))

    rows = []
    formation_id = 1
    for team_code, buckets in by_team.items():
        for bucket in buckets:
            buckets[bucket].sort(key=lambda pair: pair[1], reverse=True)

        rng = Random(f"formations-{team_code}")
        recommended = rng.choice(list(SHAPES))

        for name, shape in SHAPES.items():
            top_forward = buckets.get("FW", [("the front line", 0)])[0][0]
            top_mid = buckets.get("MF", [("midfield", 0)])[0][0]
            notes = (
                f"Recommended vs balanced opponents - built around {top_forward}'s movement "
                f"up front and {top_mid} dictating play through the middle."
                if name == recommended
                else f"Alternative shape - leans on {top_mid} in midfield if {top_forward} is unavailable."
            )
            rows.append({
                "formation_id": formation_id,
                "name": name,
                "players_json": _build_players_json(buckets, shape),
                "notes": notes,
                "suitable_vs": SUITABLE_VS[name],
                "team_code": team_code,
            })
            formation_id += 1
    return rows
