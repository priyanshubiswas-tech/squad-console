# squad-console — connective map

Start here. Every note below links back to this one.

## External APIs
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
Built so far: [[clickhouse]] schema + real data, [[ingestion]]'s ELT pipeline (real [[thesportsdb]] data + synthetic fields, host-run), [[backend-fastapi]] health-check base, a [[frontend]] placeholder page — the three containers (clickhouse/backend/frontend) wired together on one Docker network via Docker Compose, each independently health-checked; ingestion runs on the host by design, not containerized. Everything else linked above is a next-phase placeholder — see the root `README.md` roadmap for order.
