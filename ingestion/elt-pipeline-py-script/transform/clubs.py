"""Transform stage: squad_data_store.players (already loaded) -> clubs rows.

Runs after players are loaded, reading them back from ClickHouse rather than
taking Wikipedia's parsed rows in memory - keeps every stage talking through
the database, not shared Python state, which is what lets stages become
independent Airflow tasks later. `club_id` has no real numeric id behind it
(Wikipedia doesn't give one), so it's a stable hash of the club name instead.
`league` is left blank - resolving it needs an extra lookup per club, out of
scope for this pass.
"""
from transform.players import _stable_id

from config import CLICKHOUSE_MASTER_DB


def transform_all(client) -> list:
    rows_raw = client.query(
        f"SELECT DISTINCT club, team_code FROM {CLICKHOUSE_MASTER_DB}.players WHERE club != ''"
    ).result_rows

    rows = []
    for club, team_code in rows_raw:
        rows.append({
            "club_id": _stable_id(club),
            "name": club,
            "league": "",
            "team_code": team_code,
        })

    by_team = {}
    for row in rows:
        by_team.setdefault(row["team_code"], 0)
        by_team[row["team_code"]] += 1
    for team_code, count in by_team.items():
        print(f"  {team_code}: {count} distinct clubs")
    return rows
