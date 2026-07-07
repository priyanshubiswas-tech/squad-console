# Chat request flow

**Status**: describes a not-yet-built flow — see `../../architecture/diagrams.md` § 2 for the diagram version.

`POST /api/chat {message, active_team}` on [[backend-fastapi]] → [[langgraph-agent]]:

1. `intent_router` — classifies intent, extracts an opponent team from phrasing like "vs Brazil".
2. `stats_tool` — queries [[clickhouse]]: own team full, opponent team `public_stats` only.
3. `rag_retriever` — queries [[chromadb]]: `{active_team}_full` always, `{opponent_team}_public` + `shared_theory` if an opponent was extracted.
4. `access_filter` — re-applies [[access-control]] as a final check, in case anything upstream leaked something it shouldn't have.
5. `reasoner` — LLM call synthesizing stats + retrieved docs into a tactical recommendation.
6. `chart_node` (conditional) — generates a matplotlib/seaborn PNG if the intent is a comparison.
7. `composer` — returns `{text, chart_url}` to [[frontend]].

← back to [[index]]
