# frontend

Vite + React + Tailwind. The real app: login, dashboard, inspect, tactics, news, and a persistent chat panel — matching the wireframes in `../Tactica_Architecture (1).pdf` (local reference only, gitignored, see root README). Verified end-to-end in a real browser via Playwright.

This is the **only** place in the repo where the product's public brand name ("Tactica") is meant to appear — everything else (services, database names, code, docs) intentionally uses the neutral internal name `squad-console`.

## Pages

- **`Login`** — grid of 7 crest cards, tap to select (no text input). Calls `POST /api/session/select-team`, stores `{team_code, manager_name}` in `TeamContext` (localStorage-backed), navigates to `/dashboard`.
- **`Dashboard`** — own team, full data: metric cards, formation cards (recommended one highlighted), injury list, top performers, a sortable squad table.
- **`InspectSquad`** — team picker for the other 6 teams; blurred placeholders (lock icon + "Private to {team} staff") wherever the backend sent `null` for injuries/salaries/training load; formations show name + `suitable_vs` only.
- **`Tactics`** — full formation library for the active team, each with an SVG pitch diagram (`components/PitchDiagram.tsx`) built from the real `players_json` lineup.
- **`News`** — honest placeholder; the RSS fetcher isn't built yet (see root README roadmap).
- **`ChatPanel`** (persistent, every page) — 3 chips (`/api/reports/*`, zero LLM) + a free-form chatbox (`/api/chat`, the LangGraph agent - gracefully degrades without an LLM key). Both render through the same message-bubble code, since both return `{text, chart_url}`.

## Identity: cookie vs. localStorage

The backend trusts an **httpOnly** `X-Active-Team` cookie for access control - JS can't read it, by design. `TeamContext` is a separate, purely client-side mirror (localStorage) of `{team_code, manager_name}`, used only to render the header/sidebar/accent color. Both are set together in `Header.tsx`'s team-switch handler, which then does a full `window.location.href` reload (per the original spec: switching teams reloads the whole app) rather than a client-side route change, since every page's data is scoped to the active team.

## Local development (without Docker)

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_BACKEND_URL` if the backend isn't at `http://localhost:8000`, and `VITE_API_KEY` to match `.env`'s `API_KEY` (without it, every backend call 401s except `/api/health*`).

`npm run build` runs `tsc --noEmit` before `vite build` - a real type error (`import.meta.env` needing `vite-env.d.ts`) shipped silently for a while before this was added, since `vite build` alone doesn't type-check.

## Docker

Multi-stage build: `node:20-alpine` builds the static bundle (receiving `VITE_API_KEY` as a build arg from `docker-compose.yml`, since Vite bakes `VITE_*` vars in at build time), `nginx:alpine` serves it on port 80 (mapped to `3000` on the host). `nginx.conf` has a SPA fallback (`try_files $uri $uri/ /index.html`) so client-side routes survive a hard refresh.
