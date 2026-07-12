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
- [[backend-fastapi]]
- [[langgraph-agent]]
- [[frontend]]
- [[nginx]]

## End-to-end flows
- [[chat-request-flow]]
- [[access-control]]

## Current build status
Built so far: [[clickhouse]] schema + real, full 26-man squads; [[ingestion]]'s ELT pipeline (real [[wikipedia]] + [[thesportsdb]] data + synthetic fields, host-run); [[backend-fastapi]] with session/dashboard/inspect/data-sources/charts all working and access-controlled; [[nginx]] as reverse proxy with an `X-API-Key` gate (checked independently by both); a [[frontend]] placeholder page. The four containers (clickhouse/backend/frontend/nginx) are wired together on one Docker network via Docker Compose, each independently health-checked; ingestion runs on the host by design, not containerized. [[access-control]] (the data-privacy layer, separate from the API key) is implemented, not just designed. Still placeholder: [[langgraph-agent]], [[chromadb]], the real frontend UI — see the root `README.md` roadmap for order.
