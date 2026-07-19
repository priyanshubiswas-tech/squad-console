# embedding_job

Chunks and embeds `knowledge_base/` markdown into ChromaDB. Runs on the **host**, like `ingestion/elt-pipeline-py-script/` — no container, so `knowledge_base/` can be edited and re-embedded immediately.

## Collections

| Collection | Source file | `visibility` metadata |
|---|---|---|
| `{team}_full` | `knowledge_base/{team}/tactics_notes.md` | `private` |
| `{team}_public` | `knowledge_base/{team}/public_scouting.md` | `public` |
| `shared_theory` | `knowledge_base/shared/tactical_theory.md` | `public` |

Every chunk also carries `team` and `doc_type` metadata. `chunking.py` splits along markdown section headers first (each section is usually one coherent topic — one formation, one player note), falling back to paragraph-splitting only if a section is still too long for a single embedding.

## Embeddings: no LLM key needed

Uses ChromaDB's default embedding function — a local `all-MiniLM-L6-v2` sentence-transformers model, downloaded once (~80MB) on first run and cached (`~/.cache/chroma/`). This is a local model, not an API call, so this phase runs completely without `ANTHROPIC_API_KEY`/`OPENAI_API_KEY`, matching the rest of this project's build order.

## Running it

```bash
cd embedding_job
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python embed_team_docs.py
```

Requires the `chroma` container running (`docker compose up -d chroma`) and reachable on `localhost:8001` (the host-published port — see `CHROMA_HOST_PORT` in `.env`; distinct from `CHROMA_PORT=8000`, which is what the *backend container* will use over the in-network hostname `chroma`).

Every run does a full delete-and-re-add per collection, so editing a knowledge_base file and re-running never leaves stale chunks behind — safe to re-run any time.

## Verifying it worked

```bash
python3 -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8001)
for c in client.list_collections():
    print(c.name, c.count())
"
```

Or run an actual semantic search to sanity-check retrieval quality:

```bash
python3 -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8001)
coll = client.get_collection('england_full')
r = coll.query(query_texts=['what happens if a key defender is missing'], n_results=2)
print(r['documents'][0][0][:300])
"
```
