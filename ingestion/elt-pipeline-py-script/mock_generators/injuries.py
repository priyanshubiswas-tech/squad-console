"""Never had a free source, real or otherwise - always synthetic. 2-4
injured players per team, picked deterministically per team so re-runs are
reproducible before real-time ingestion exists.
"""
from datetime import date, timedelta
from random import Random

from config import CLICKHOUSE_MASTER_DB

INJURY_TYPES = ["Hamstring strain", "Ankle sprain", "Knee ligament", "Groin strain", "Calf strain", "Muscle fatigue"]
STATUSES = ["Out", "Doubtful", "Recovering"]
SEVERITIES = ["Minor", "Moderate", "Severe"]


def generate(client) -> list:
    players = client.query(f"SELECT player_id, team_code FROM {CLICKHOUSE_MASTER_DB}.players").result_rows
    by_team = {}
    for player_id, team_code in players:
        by_team.setdefault(team_code, []).append(player_id)

    rows = []
    for team_code, player_ids in by_team.items():
        team_rng = Random(f"injuries-{team_code}")
        count = team_rng.randint(2, min(4, len(player_ids))) if player_ids else 0
        for player_id in team_rng.sample(player_ids, count):
            rng = Random(player_id)
            rows.append({
                "player_id": player_id,
                "injury_type": rng.choice(INJURY_TYPES),
                "status": rng.choice(STATUSES),
                "expected_return": date.today() + timedelta(days=rng.randint(3, 60)),
                "severity": rng.choice(SEVERITIES),
                "team_code": team_code,
            })
    return rows
