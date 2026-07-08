"""Real wages aren't published anywhere free - always synthetic, deterministic per player_id."""
from datetime import date
from random import Random

from config import CLICKHOUSE_MASTER_DB


def generate(client) -> list:
    players = client.query(f"SELECT player_id, team_code FROM {CLICKHOUSE_MASTER_DB}.players").result_rows
    rows = []
    for player_id, team_code in players:
        rng = Random(player_id)
        rows.append({
            "player_id": player_id,
            "weekly_wage": rng.randint(15_000, 350_000),
            "contract_until": date(rng.randint(2026, 2030), rng.randint(1, 12), rng.randint(1, 28)),
            "team_code": team_code,
        })
    return rows
