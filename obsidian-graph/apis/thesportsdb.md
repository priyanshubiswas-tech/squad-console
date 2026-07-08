# TheSportsDB

**Status**: built and live — real data for all 7 teams as of this pass.

Free, public test key `3`, no signup needed. National teams (not just clubs) are covered: team lookup, real squad lists (name/position/club/age/nationality/photo), and real recent match results — including live tournament fixtures.

- Team id resolution: `searchteams.php?t={name}` filtered to `strSport == "Soccer"`, `strGender == "Male"`, `"FIFA World Cup" in strLeague` — unambiguous for all 7 teams tested.
- Squad endpoint (`lookup_all_players.php`) also returns coaching staff attached to the national team entity itself; [[ingestion]] filters to entries where `idTeam2` (the national-team link) is set, since staff don't have it.
- Honours endpoint returns nothing for national teams — trophies are hand-curated real facts instead, not fetched from here.
- Feeds into: [[ingestion]] → `raw_data_store` (raw dump) → [[clickhouse]] `players`/`clubs`/`matches`
- Also used by: [[frontend]] login page (crest images, `strBadge`) once it's built
- Env var: `THESPORTSDB_KEY` in `.env` (default `3`)

← back to [[index]]
