"""Never had a free source - always synthetic. 4 weeks per player, deterministic per player_id."""
from random import Random

from config import CLICKHOUSE_MASTER_DB


def generate(client) -> list:
    players = client.query(f"SELECT player_id, team_code FROM {CLICKHOUSE_MASTER_DB}.players").result_rows
    rows = []
    for player_id, team_code in players:
        rng = Random(player_id)
        for week_no in range(1, 5):
            rows.append({
                "player_id": player_id,
                "week_no": week_no,
                "load_score": round(rng.uniform(200, 800), 1),
                "fatigue_index": round(rng.uniform(0.1, 0.9), 2),
                "team_code": team_code,
            })
    return rows
