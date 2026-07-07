# frontend

**Status**: minimal Vite + React + Tailwind placeholder built this pass — a single page proving container-to-container connectivity, not the real app.

The **only** place the product's public brand name is meant to appear — everything else in this repo intentionally uses the neutral name `squad-console`. Real build will be React + Tailwind, dark football theme (see `../../architecture/ARCHITECTURE.md` § Design system).

Talks directly to [[backend-fastapi]] (`VITE_BACKEND_URL`, default `http://localhost:8000`) for now; will be proxied by [[nginx]] once that's built. Login page will use [[thesportsdb]] crest images; dashboard/inspect pages will render [[access-control]]'s redacted fields as blurred placeholders; chat panel will render [[langgraph-agent]] responses inline, including chart PNGs.

← back to [[index]]
