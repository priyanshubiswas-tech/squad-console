# TheSportsDB

**Status**: built and live — real match results for all 8 teams, plus a photo backfill for players also in [[wikipedia]]'s squad list.

Free, public test key `3`, no signup needed. National teams (not just clubs) are covered: team lookup, squad lists, and real recent match results — including live tournament fixtures.

- Team id resolution: `searchteams.php?t={name}` filtered to `strSport == "Soccer"`, `strGender == "Male"`, `"FIFA World Cup" in strLeague` — unambiguous for all 8 teams tested.
- Squad endpoint (`lookup_all_players.php`) only has ~9-10 currently-tagged players per national team - real, but not a full squad, and also returns coaching staff attached to the national team entity itself (filtered via `idTeam2`). [[wikipedia]] is the primary source for the full 26-man squad; this endpoint is now used only to backfill real photo URLs by name match.
- Honours endpoint returns nothing for national teams — trophies are hand-curated real facts instead, not fetched from here.
- Feeds into: [[ingestion]] → `raw_data_store` (raw dump) → [[clickhouse]] `matches` (real) + `players.photo_url` (partial backfill)
- Also used by: [[frontend]] login page (crest images, `strBadge`) once it's built
- Env var: `THESPORTSDB_KEY` in `.env` (default `3`)

← back to [[index]]
