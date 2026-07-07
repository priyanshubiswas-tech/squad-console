# nginx

**Status**: not built yet — placeholder, added once [[frontend]] exists.

Reverse proxy: `/api/*` → [[backend-fastapi]], everything else → the built [[frontend]] static bundle. Single entrypoint on port 80 in production; until then, the backend and frontend dev servers are reached directly on their own ports.

← back to [[index]]
