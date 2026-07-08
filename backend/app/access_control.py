"""Single source of truth for what's visible about a team's squad.

Used by both the REST `inspect` router and (later) the LangGraph
`access_filter` node - never duplicate this logic anywhere else. See
architecture/ARCHITECTURE.md § Access control for the table this encodes.
"""

FULL = "full"
BLOCKED = "blocked"
PARTIAL = "partial"

TABLE_RULES = {
    "players": FULL,
    "public_stats": FULL,
    "clubs": FULL,
    "trophies": FULL,
    "matches": FULL,
    "injuries": BLOCKED,
    "salaries": BLOCKED,
    "training_load": BLOCKED,
    "formations": PARTIAL,
}

# Which columns survive when a table's access level is "partial". Per-team
# databases don't carry team_code on every table (only `players` does - see
# database/clickhouse/README.md), so it's deliberately not listed here.
PARTIAL_COLUMNS = {
    "formations": ["formation_id", "name", "suitable_vs"],
}


def get_allowed_tables(requested_team: str, active_team: str) -> dict:
    """{table_name: "full" | "blocked" | "partial"} for every table.

    Own team (requested_team == active_team) always gets full access to
    everything. Any other team falls back to TABLE_RULES - public fields
    stay full, private fields are blocked, formations are partial.
    """
    if requested_team == active_team:
        return {table: FULL for table in TABLE_RULES}
    return dict(TABLE_RULES)


def allowed_columns(table: str, access: str) -> list | None:
    """None means "select every column"; a list restricts to just those.

    Only meaningful for "partial" tables - "blocked" tables aren't queried
    at all (the caller returns null for that field instead), and "full"
    tables have no column restriction.
    """
    if access == PARTIAL:
        return PARTIAL_COLUMNS.get(table)
    return None
