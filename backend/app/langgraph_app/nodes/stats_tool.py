"""ClickHouse read: own team gets everything, an opponent (if named in the
query) only ever gets public_stats - matches access_control.py's matrix,
re-checked defensively by access_filter downstream.
"""
from app.db.clickhouse_client import get_client


def stats_tool(state: dict) -> dict:
    client = get_client()
    team = state["active_team"]

    players = client.query(
        f"SELECT name, position, overall_rating FROM {team}.players ORDER BY overall_rating DESC"
    ).result_rows
    public_stats = client.query(f"""
        SELECT p.name, s.goals, s.assists, s.rating_avg
        FROM {team}.public_stats s JOIN {team}.players p ON p.player_id = s.player_id
        ORDER BY s.rating_avg DESC
    """).result_rows
    formations = client.query(
        f"SELECT name, players_json, notes, suitable_vs FROM {team}.formations"
    ).result_rows

    own_stats = {
        "players": players,
        "public_stats": public_stats,
        "formations": formations,
    }

    opponent_public_stats = {}
    opponent_team = state.get("opponent_team")
    if opponent_team:
        rows = client.query(f"""
            SELECT p.name, s.goals, s.assists, s.rating_avg
            FROM {opponent_team}.public_stats s JOIN {opponent_team}.players p ON p.player_id = s.player_id
            ORDER BY s.rating_avg DESC
            LIMIT {{limit:UInt8}}
        """, parameters={"limit": 10}).result_rows
        opponent_public_stats = {"public_stats": rows}

    return {**state, "own_stats": own_stats, "opponent_public_stats": opponent_public_stats}
