# LangGraph agent

**Status**: not built yet — placeholder for the RAG phase. Needs an LLM key (`ANTHROPIC_API_KEY` or `OPENAI_API_KEY`), which is intentionally the very last thing added to this project.

Powers "Ask the analyst" via [[backend-fastapi]]'s `chat` router. Full node-by-node flow: see [[chat-request-flow]].

Nodes, in order: `intent_router → stats_tool → rag_retriever → access_filter → reasoner → [chart_node?] → composer`.
- `stats_tool` reads [[clickhouse]]
- `rag_retriever` reads [[chromadb]]
- `access_filter` re-applies the same function [[access-control]] describes — single source of truth, never duplicated
- `chart_node` (conditional) generates matplotlib/seaborn PNGs

← back to [[index]]
