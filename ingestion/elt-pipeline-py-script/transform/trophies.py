"""Transform stage: hand-curated real major honours -> squad_data_store.trophies rows.

Not fetched from an API - TheSportsDB's honours endpoint returns nothing
for these national teams. This is still real, factual data; it's just
authored in fixtures/trophies.json instead of pulled live. `client` is
accepted (and unused) purely so every transform stage shares the same
transform_all(client) signature, which keeps the orchestrator's loop simple.
"""
import json
from pathlib import Path

from config import TEAMS

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "trophies.json"


def transform_all(client) -> list:
    data = json.loads(FIXTURE_PATH.read_text())
    rows = []
    trophy_id = 1
    for team_code in TEAMS:
        for trophy in data.get(team_code, []):
            rows.append({
                "trophy_id": trophy_id,
                "name": trophy["name"],
                "year": trophy["year"],
                "team_code": team_code,
            })
            trophy_id += 1
    print(f"  loaded {len(rows)} curated real trophies across {len(TEAMS)} teams")
    return rows
