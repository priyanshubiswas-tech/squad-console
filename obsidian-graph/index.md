# squad-console — connective map

Start here. Every note below links back to this one.

## External APIs
- [[wikipedia]]
- [[api-football]]
- [[thesportsdb]]
- [[transfermarkt]]
- [[newsapi-rss]]

## Data stores
- [[clickhouse]]
- [[chromadb]]

## Services
- [[ingestion]]
- [[embedding-job]]
- [[backend-fastapi]]
- [[langgraph-agent]]
- [[frontend]]
- [[nginx]]

## End-to-end flows
- [[chat-request-flow]]
- [[access-control]]

## Current build status
Built so far: [[clickhouse]] schema + real, full 26-man squads; [[ingestion]]'s ELT pipeline (real [[wikipedia]] + [[thesportsdb]] data + synthetic fields, host-run); real, researched knowledge-base content for all 7 teams, chunked and embedded into [[chromadb]] (15 collections) via [[embedding-job]] (host-run, local embedding model, no LLM key); [[backend-fastapi]] with session/dashboard/inspect/data-sources/charts/reports all working and access-controlled; [[nginx]] as reverse proxy with an `X-API-Key` gate (checked independently by both); a [[frontend]] placeholder page. The five containers (clickhouse/chroma/backend/frontend/nginx) are wired together on one Docker network via Docker Compose, each independently health-checked; ingestion and embedding both run on the host by design, not containerized. [[access-control]] (the data-privacy layer, separate from the API key) is implemented, not just designed. [[chat-request-flow]]'s Path A (3 zero-LLM chip reports) is built; Path B (free-form LangGraph chat, which will query the now-embedded ChromaDB collections) is the one remaining phase, and the only one that needs an LLM key. Still placeholder: [[langgraph-agent]], the real frontend UI — see the root `README.md` roadmap for order.
