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
Built so far: [[clickhouse]] schema + real, full 26-man squads; [[ingestion]]'s ELT pipeline (real [[wikipedia]] + [[thesportsdb]] data + synthetic fields, host-run); [[backend-fastapi]] with session/dashboard/inspect/data-sources/charts all working and access-controlled; a [[frontend]] placeholder page. The three containers (clickhouse/backend/frontend) are wired together on one Docker network via Docker Compose, each independently health-checked; ingestion runs on the host by design, not containerized. [[access-control]] is implemented, not just designed. Still placeholder: [[langgraph-agent]], [[chromadb]], the real frontend UI, [[nginx]] — see the root `README.md` roadmap for order.
