# Wikipedia

**Status**: built and live — primary source for real, full 26-man squads.

Free, no key, no signup. The "2026 FIFA World Cup squads" article has one section per team, each a consistent wikitext template (`{{nat fs g player|...}}`) — name, position, club, birth date, one line per player. Parsed with a small tokenizer that respects `[[wikilink|display]]` nesting (a naive `split("|")` breaks on the pipe inside a link).

- Section index is resolved by team display name at fetch time (`action=parse&prop=sections`), not hardcoded — page structure can change between tournaments.
- Requires a descriptive `User-Agent` header — Wikimedia's API 403s the default `requests` UA. See [[thesportsdb]] for the complementary role: TheSportsDB only has ~9-10 currently-tagged players per national team, so Wikipedia is the primary squad source and TheSportsDB backfills real photos by name match.
- Feeds into: [[ingestion]] → `raw_data_store` (entity `wikipedia_squad`) → [[clickhouse]] `players` (real fields) + `clubs` (derived)

← back to [[index]]
