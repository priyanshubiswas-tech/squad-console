# frontend

**Status**: built. Vite + React + Tailwind, dark football theme (see `../../architecture/ARCHITECTURE.md` § Design system). Verified end-to-end in a real browser via Playwright.

The **only** place the product's public brand name is meant to appear — everything else in this repo intentionally uses the neutral name `squad-console`.

Pages: `Login` (7 crests, no text input), `Dashboard` (own team, full data), `InspectSquad` (redacted view of other teams, blurred placeholders per [[access-control]]), `Tactics` (SVG pitch diagrams built from real `players_json`), `News` (honest placeholder), and a persistent `ChatPanel` on every page - 3 chips (`/api/reports/*`) + a free-form chatbox (`/api/chat`, [[langgraph-agent]]), both rendering through the same message-bubble code since both return `{text, chart_url}`.

Talks directly to [[backend-fastapi]] (`VITE_BACKEND_URL`, default `http://localhost:8000`); also reachable via [[nginx]]. Team identity: the backend trusts an httpOnly cookie (JS can't read it); the frontend keeps its own localStorage mirror (`TeamContext`) purely for rendering the header/manager/accent color, kept in sync because both are set together on login/switch.

← back to [[index]]
