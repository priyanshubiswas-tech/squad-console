# LangGraph agent

**Status**: built. Real `langgraph` `StateGraph`, 7 nodes, wired to [[backend-fastapi]]'s `POST /api/chat`. Only the `reasoner` node needs an LLM key (`ANTHROPIC_API_KEY` or `OPENAI_API_KEY`) - it gracefully degrades to an honest fallback message when one isn't configured, rather than erroring, so every other node still runs against real data on every call.

Lives in `backend/app/langgraph_app/`. Full node-by-node flow: see [[chat-request-flow]].

Nodes, in order: `intent_router → stats_tool → rag_retriever → access_filter → reasoner → [chart_node?] → composer`.
- `intent_router` — keyword-based (no LLM), classifies intent + extracts an opponent team name.
- `stats_tool` reads [[clickhouse]] - own team full, opponent `public_stats` only.
- `rag_retriever` reads [[chromadb]] - `{active}_full` always, `{opponent}_public` + `shared_theory` if named.
- `access_filter` re-applies the same function [[access-control]] describes — single source of truth, never duplicated.
- `reasoner` — the only LLM call. Falls back gracefully without a key.
- `chart_node` (conditional, `comparison` intent) — calls `app/charts/generators.py::team_comparison_chart`, the same function a chip could call. Never depends on the LLM.
- `composer` — assembles `{text, chart_url}`.

Verified live: all 4 of the original spec's test prompts run end-to-end (formation-vs-opponent, stat lookup, comparison-with-chart, opponent-injury-privacy) - see `backend/README.md` for the exact prompts.

← back to [[index]]
