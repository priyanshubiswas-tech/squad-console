# ChromaDB

**Status**: not wired up yet — placeholder for the RAG phase.

The vector store for tactical knowledge. Populated by [[embedding_job]] reading `knowledge_base/`, queried by [[langgraph-agent]]'s `rag_retriever` node.

## Planned collections
- `{team}_full` — embeds `knowledge_base/{team}/tactics_notes.md`. Only ever queried when that team is the *active* team.
- `{team}_public` — embeds `knowledge_base/{team}/public_scouting.md`. Queried when that team is the *opponent*.
- `shared_theory` — embeds `knowledge_base/shared/tactical_theory.md`. Always queryable.

Every chunk carries `{team, doc_type, visibility}` metadata — [[access-control]]'s `access_filter` node re-checks this metadata as a defense-in-depth layer, even though the collection split should already prevent leaks.

## Persistence
Planned named Docker volume `chroma_data` (not declared yet — added when this service is built). `knowledge_base/` itself is a bind mount, not baked into an image, so tactical notes can be edited live and re-embedded without a rebuild.

← back to [[index]]
