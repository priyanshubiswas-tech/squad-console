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
Everything is built except real news and a real LLM key. [[clickhouse]] schema + real, full 26-man squads; [[ingestion]]'s ELT pipeline (real [[wikipedia]] + [[thesportsdb]] data + synthetic fields, host-run); real, researched knowledge-base content for all 7 teams, chunked and embedded into [[chromadb]] (15 collections) via [[embedding-job]] (host-run, local embedding model, no LLM key); [[backend-fastapi]] with session/dashboard/inspect/data-sources/charts/reports/chat all working and access-controlled; [[langgraph-agent]]'s full 7-node graph runs on every chat call, gracefully degrading only at the `reasoner` node without an LLM key; the real [[frontend]] (login/dashboard/inspect/tactics/news + persistent chat panel), verified end-to-end in a real browser via Playwright; [[nginx]] as reverse proxy with an `X-API-Key` gate (checked independently by both). Five containers (clickhouse/chroma/backend/frontend/nginx) wired together on one Docker network, each independently health-checked; ingestion and embedding both run on the host by design, not containerized. [[access-control]] (the data-privacy layer, separate from the API key) is enforced end-to-end, in both REST and chat paths. [[chat-request-flow]]'s Path A (chips) and Path B (LangGraph chat) are both built and render through one identical frontend code path. Still open: real `news` (RSS not built), an LLM key (last thing added, per the original plan), Airflow scheduling, and closing the direct backend/frontend ports for a real deployment — see the root `README.md` roadmap.
