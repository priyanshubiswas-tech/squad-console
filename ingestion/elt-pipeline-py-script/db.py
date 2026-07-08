import clickhouse_connect

from config import (
    CLICKHOUSE_HOST,
    CLICKHOUSE_PASSWORD,
    CLICKHOUSE_PORT,
    CLICKHOUSE_USER,
)


def get_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
    )


def get_latest_raw(client, team_code: str, entity: str) -> str:
    """Read back the most recent raw dump for a team/entity pair.

    Transform stages go through this instead of taking data handed to them
    in-memory by the fetch stage, so fetch and transform stay independent -
    the only thing that couples them is raw_data_store. That's what lets them
    become separate Airflow tasks later without a rewrite.
    """
    result = client.query(
        """
        SELECT payload FROM raw_data_store.thesportsdb_dumps
        WHERE team_code = {team_code:String} AND entity = {entity:String}
        ORDER BY fetched_at DESC
        LIMIT 1
        """,
        parameters={"team_code": team_code, "entity": entity},
    )
    if not result.result_rows:
        raise RuntimeError(f"No raw '{entity}' dump found for team '{team_code}' - run the fetch stage first.")
    return result.result_rows[0][0]
