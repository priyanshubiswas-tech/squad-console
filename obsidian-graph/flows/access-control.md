# Access control

**Status**: built - `backend/app/access_control.py`, live in production traffic through the `inspect` router.

The single privacy rule the whole system depends on, and the one piece of logic that must never be duplicated. See `../../architecture/ARCHITECTURE.md` § Access control and `../../architecture/diagrams.md` § 4 for the matrix.

One function decides what's visible: `get_allowed_tables(requested_team, active_team)`. Two callers, same function:
- [[backend-fastapi]]'s `inspect` router (REST path) - built
- [[langgraph-agent]]'s `access_filter` node (chat path) - not built yet, will call the identical function

Rule: own team's `players`, `public_stats`, `clubs`/`trophies`/`matches`, `injuries`, `salaries`, `training_load`, `formations` are all full access. For any *other* team: everything public-facing stays full, but `injuries`/`salaries`/`training_load` return `null` (never omitted — [[frontend]] needs the key present to render a blur placeholder), and `formations` drops everything except `name` + `suitable_vs`.

Backed by data in [[clickhouse]] (structured fields) and [[chromadb]] (document `visibility` metadata).

← back to [[index]]
