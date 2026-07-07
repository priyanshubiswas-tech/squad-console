# TheSportsDB

**Status**: not wired up yet — placeholder for the ingestion phase.

Free, public test key `3`. Source of squad lists, player profiles, photos, and team crests/badges.

- Feeds into: [[ingestion]] → [[clickhouse]] (`players` basic fields, photo URLs)
- Also used by: [[frontend]] login page (crest images) once it's built
- Env var: `THESPORTSDB_KEY` in `.env` (default `3` works for testing, no signup needed)

← back to [[index]]
