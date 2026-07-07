# frontend

Minimal Vite + React + Tailwind placeholder — proves the frontend container can reach the backend/ClickHouse over the `squadnet` Docker network. Not the real app yet (no login, dashboard, or chat) — see the root `README.md` roadmap.

This is the **only** place in the repo where the product's public brand name ("Tactica") is meant to appear — everything else (services, database names, code, docs) intentionally uses the neutral internal name `squad-console`.

## Local development (without Docker)

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_BACKEND_URL` if the backend isn't at `http://localhost:8000`.

## Docker

Multi-stage build: `node:20-alpine` builds the static bundle, `nginx:alpine` serves it on port 80 (mapped to `3000` on the host by `docker-compose.yml`).
