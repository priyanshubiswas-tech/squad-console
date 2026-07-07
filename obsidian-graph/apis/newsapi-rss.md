# RSS feeds / NewsAPI

**Status**: not wired up yet — placeholder for the ingestion phase.

RSS from BBC Sport / Sky Sports / ESPN preferred over NewsAPI's free tier for reliability (no daily cap, no key required). Source of trending news per team.

- Feeds into: [[ingestion]] → surfaces on the "News & trends" page in [[frontend]]
- Env var: `NEWSAPI_KEY` in `.env` (optional fallback; RSS fetchers need no key)

← back to [[index]]
