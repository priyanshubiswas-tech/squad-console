"""Partition stage: fan squad_data_store (master) out into the 7 per-team
databases, truncate-and-reload per table. Column list per table is read via
DESCRIBE TABLE rather than hardcoded, since the per-team schema differs from
the master by exactly the team_code column (present only on `players`) -
this way the fan-out never drifts out of sync with database/clickhouse/init/.
"""
from config import CLICKHOUSE_MASTER_DB, TEAMS

TABLES = [
    "players", "public_stats", "injuries", "salaries",
    "training_load", "formations", "clubs", "trophies", "matches",
]


def _team_columns(client, team_code: str, table: str) -> list:
    result = client.query(f"DESCRIBE TABLE {team_code}.{table}")
    return [row[0] for row in result.result_rows]


def partition_all(client) -> None:
    print(f"Partition: fanning {CLICKHOUSE_MASTER_DB} out into {len(TEAMS)} team DBs")
    for team_code in TEAMS:
        for table in TABLES:
            columns = _team_columns(client, team_code, table)
            select_cols = ", ".join(columns)
            client.command(f"TRUNCATE TABLE {team_code}.{table}")
            client.command(
                f"""
                INSERT INTO {team_code}.{table}
                SELECT {select_cols} FROM {CLICKHOUSE_MASTER_DB}.{table}
                WHERE team_code = {{team_code:String}}
                """,
                parameters={"team_code": team_code},
            )
        count = client.query(f"SELECT count() FROM {team_code}.players").result_rows[0][0]
        print(f"  {team_code}: {count} players")
