"""No free source without a paid API-Football key. Deterministic synthetic
stats seeded per real player_id, so re-running the pipeline before that key
exists reproduces the same numbers rather than drifting each time.
"""
from random import Random

from config import CLICKHOUSE_MASTER_DB


def generate(client) -> list:
    players = client.query(f"SELECT player_id, team_code FROM {CLICKHOUSE_MASTER_DB}.players").result_rows
    rows = []
    for player_id, team_code in players:
        rng = Random(player_id)
        rows.append({
            "player_id": player_id,
            "goals": rng.randint(0, 20),
            "assists": rng.randint(0, 15),
            "key_passes": rng.randint(0, 60),
            "tackles": rng.randint(0, 80),
            "rating_avg": round(rng.uniform(6.0, 8.5), 2),
            "matches_played": rng.randint(5, 38),
            "team_code": team_code,
        })
    return rows
