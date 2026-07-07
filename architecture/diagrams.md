# Diagrams

## 1. High-level architecture

```mermaid
flowchart TB
    subgraph ext["External data sources (free APIs)"]
        api1["API-Football"]
        api2["TheSportsDB"]
        api3["Transfermarkt"]
        api4["RSS / NewsAPI"]
        mock["Mock generators\n(injuries, salaries, training load, tactics)"]
    end

    ingest["Ingestion layer\n(Python + APScheduler)"]
    ext --> ingest

    subgraph ch["ClickHouse"]
        master["squad_data_store\n(master, PARTITION BY team_code)"]
        teamdbs["Per-team DBs\nengland / france / brazil / argentina / spain / germany / portugal"]
        partition["partition.py\n(fan-out master -> team DBs)"]
        master --> partition --> teamdbs
    end
    ingest --> master

    subgraph rag["RAG + agent layer"]
        embed["Embedding job\n(per-team docs -> Chroma)"]
        chroma["ChromaDB\nper-team collections (full + public)"]
        agent["LangGraph agent\nintent -> stats -> RAG -> access_filter -> reason -> chart"]
        chart["Chart generator\n(matplotlib/seaborn)"]
        embed --> chroma --> agent --> chart
    end

    subgraph serve["Serving layer"]
        backend["FastAPI backend\nREST + access control + LangGraph endpoint"]
        frontend["Frontend\nReact + Tailwind"]
        nginx["Nginx\nreverse proxy + static"]
    end

    teamdbs -->|"read, scoped by active team"| backend
    master -->|"cross-team analytics"| backend
    agent --> backend
    backend <-->|"team_context header"| frontend
    nginx --- backend
    nginx --- frontend
```

## 2. Chatbot request flow (LangGraph)

```mermaid
flowchart TB
    req["POST /api/chat {message, active_team}\nheader: X-Active-Team"]
    n1["1. intent_router\nclassify intent + extract opponent team"]
    n2["2. stats_tool\nClickHouse query"]
    ownDb["own team DB\n(players, public_stats, injuries,\nsalaries, training_load, formations) -> FULL"]
    oppDb["opponent DB\n-> public_stats, players, clubs, trophies only"]
    n3["3. rag_retriever\nChromaDB query"]
    ownColl["{active_team}_full collection"]
    oppColl["{opponent_team}_public + shared_theory"]
    n4["4. access_filter\nstrip any disallowed fields/snippets\n(defense in depth)"]
    n5["5. reasoner (LLM)\nsynthesize stats + tactical docs -> formation recommendation"]
    dec{"needs chart?"}
    n6["6. chart_node\nmatplotlib/seaborn -> save PNG"]
    n7["7. composer\nbuild {text, chart_url}"]
    resp["Response to frontend\nrendered as chat bubble + inline image"]

    req --> n1 --> n2
    n2 --> ownDb
    n2 -->|"only if opponent_team set"| oppDb
    ownDb --> n3
    oppDb --> n3
    n3 --> ownColl
    n3 --> oppColl
    ownColl --> n4
    oppColl --> n4
    n4 --> n5 --> dec
    dec -->|"yes"| n6 --> n7
    dec -->|"no"| n7
    n7 --> resp
```

## 3. Container & persistence layout

```mermaid
flowchart LR
    manager["Manager (browser)\nlocalhost"]
    nginx["nginx\nreverse proxy"]
    backend["backend (FastAPI)\nREST + LangGraph"]
    frontend["frontend\n(React + nginx-served build)"]
    ingestion["ingestion\n(APScheduler container)"]
    embedjob["embedding_job\n(Chroma embed worker)"]
    clickhouse["clickhouse-server"]
    chroma["chromadb"]
    chData["volume: clickhouse_data"]
    chrData["volume: chroma_data"]
    chartsData["volume: charts_data"]
    kb["bind mount: ./knowledge_base"]

    manager --> nginx
    nginx -->|"/api/*"| backend
    nginx --> frontend
    backend --> clickhouse
    backend --> chroma
    ingestion --> clickhouse
    embedjob --> chroma
    embedjob --- kb
    backend --> chartsData
    clickhouse --- chData
    chroma --- chrData
```

**Persistence rule**: `docker compose stop` / `start` preserves every named volume. Only `docker compose down -v` removes them. This pass only stands up `clickhouse_data` (for the `clickhouse` + `backend` services) — `chroma_data` and `charts_data` get added in their respective phases.

## 4. Access control matrix

| Table | Active team (own data) | Other team (inspect mode) |
|---|---|---|
| `players` (basic fields) | Full | Full |
| `public_stats` | Full | Full |
| `clubs` / `trophies` / `matches` | Full | Full |
| `injuries` | Full | Blocked → `null` |
| `salaries` | Full | Blocked → `null` |
| `training_load` | Full | Blocked → `null` |
| `formations` | Full | `name` + `suitable_vs` only |
