"""Parsing helpers shared by more than one transform stage."""


def real_squad_entries(entries: list) -> list:
    """Filter TheSportsDB's squad response down to actually-capped players.

    The endpoint also returns coaching staff attached to the national team
    entity itself. A real capped player has idTeam2 set to the (shared)
    national team id; staff entries don't have it set at all.
    """
    national_team_id = next((e["idTeam2"] for e in entries if e.get("idTeam2")), None)
    if national_team_id is None:
        return []
    return [e for e in entries if e.get("idTeam2") == national_team_id]
