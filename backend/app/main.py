from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import chat, charts, dashboard, data_sources, health, inspect, reports, session

app = FastAPI(title="squad-console backend")

app.add_middleware(
    CORSMiddleware,
    # Session uses an httpOnly cookie, and wildcard origins can't be
    # combined with allow_credentials (browsers reject it) - so this has to
    # be an explicit origin list (CORS_ORIGINS env var), not "*".
    allow_origins=get_settings().cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(session.router)
app.include_router(dashboard.router)
app.include_router(inspect.router)
app.include_router(data_sources.router)
app.include_router(charts.router)
app.include_router(reports.router)
app.include_router(chat.router)
