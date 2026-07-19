# Chat request flow

The chat window has two independent paths that both end up rendering the same `{text, chart_url}` shape - that equivalence is the whole "hybrid" idea:

## Path A: chips (built, zero LLM)

Three quick-reply buttons above the chatbox, always about the active team - see [[backend-fastapi]]'s `/api/reports/*`:

`Click chip → GET /api/reports/{fitness|top-performers|financial} → query ClickHouse directly (team-scoped, see [[access-control]] for which fields are private) → fill a FIXED text template with the live numbers → generate a chart via app/charts/generators.py → return {text, chart_url}`

No LLM call, no tokens, answers instantly, numbers are always current as of the last `deploy_elt.py` run.

## Path B: free-form chat (built)

`POST /api/chat {message}` on [[backend-fastapi]] (active team from the cookie, not the body) → [[langgraph-agent]]:

1. `intent_router` — classifies intent, extracts an opponent team from phrasing like "vs Brazil". Keyword-based, no LLM.
2. `stats_tool` — queries [[clickhouse]]: own team full, opponent team `public_stats` only.
3. `rag_retriever` — queries [[chromadb]]: `{active_team}_full` always, `{opponent_team}_public` + `shared_theory` if an opponent was extracted.
4. `access_filter` — re-applies [[access-control]] as a final check, in case anything upstream leaked something it shouldn't have.
5. `reasoner` — LLM call synthesizing stats + retrieved docs into a tactical recommendation. **Gracefully degrades** to an honest "no LLM key configured" message if none is set, rather than erroring - steps 1-4 and 6 still ran against real data regardless.
6. `chart_node` (conditional) — calls the *same* `app/charts/generators.py` functions Path A uses, if the intent is a comparison. Never depends on the LLM.
7. `composer` — returns `{text, chart_url}` to [[frontend]] — identical shape to Path A, so the chat window doesn't need to know or care which path answered.

Verified live end-to-end, including that opponent injury/salary/training-load data is structurally never fetched by `stats_tool` in the first place (not just filtered) - see `backend/README.md` for the 4 test prompts run.

← back to [[index]]
