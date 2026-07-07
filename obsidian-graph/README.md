# obsidian-graph

A small Obsidian vault documenting how `squad-console`'s pieces connect — which API feeds which table, which service reads which database, which flow ties it all together. It's plain markdown with `[[double-bracket links]]`, so it renders fine on GitHub too; opening this folder as an Obsidian vault additionally gives you the visual graph view.

## How to open it

1. Obsidian → "Open folder as vault" → select this `obsidian-graph/` folder.
2. Open `index.md` — it links out to every note.
3. Use the graph view (Ctrl/Cmd+G) to see the whole map at once.

## Layout

- `index.md` — hub note, links to everything below.
- `apis/` — one note per external data source and what it's used for.
- `data/` — the two datastores (ClickHouse, ChromaDB) and what lives in each.
- `services/` — one note per running/planned service (ingestion, backend, LangGraph agent, frontend, nginx).
- `flows/` — end-to-end request flows (chat, access control) that cut across multiple services.

A note here that links to a page that doesn't exist yet (shown as an unlinked/red link in Obsidian) marks something intentionally left for a later phase — see the root `README.md` roadmap.
