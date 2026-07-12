# nginx

**Status**: built - `nginx/templates/default.conf.template`, rendered via the official image's automatic `envsubst` step at container start.

Reverse proxy: `/api/*` → [[backend-fastapi]] (behind the `X-API-Key` gate, see [[access-control]] for the data-privacy layer this is separate from), `/api/charts/file/*` → backend ungated (serves a plain PNG, no custom headers possible from `<img src>`), everything else → the [[frontend]] static bundle.

- The API key is checked **twice**: once here, once again independently inside the backend (`app/deps.py::require_api_key`) - defense in depth, since `backend`'s port `8000` is still published directly to the host for dev convenience right now, which would otherwise bypass this entirely.
- The real secret (`API_KEY` in `.env`) never gets hardcoded into the committed template - `${API_KEY}` is substituted from the container's own environment at startup.
- Not yet the *only* way in - see the root README's Roadmap for closing the direct backend/frontend ports once this becomes a real deployment.

← back to [[index]]
