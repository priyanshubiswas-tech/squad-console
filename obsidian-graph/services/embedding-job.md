# embedding_job

**Status**: built — `embed_team_docs.py`, run manually on the host (same pattern as [[ingestion]]: not containerized, so `knowledge_base/` can be edited and re-embedded with no image in the loop).

Reads `knowledge_base/{team}/tactics_notes.md` + `public_scouting.md` for all 7 teams plus `knowledge_base/shared/tactical_theory.md`, chunks each along markdown section headers (`chunking.py`), and embeds into [[chromadb]] using Chroma's default local sentence-transformers model (`all-MiniLM-L6-v2`) — no LLM API call, no key needed.

Every run is a full delete-and-re-add per collection, so it's safe to re-run any time after editing `knowledge_base/` content. Connects to Chroma's host-published port (`8001`), not the in-network hostname `chroma` the backend container will eventually use — same host-vs-container distinction [[ingestion]] makes for ClickHouse.

Not consumed by anything yet — [[langgraph-agent]]'s `rag_retriever` node is the planned reader.

← back to [[index]]
