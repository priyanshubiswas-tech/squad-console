from functools import lru_cache

import chromadb

from app.config import get_settings


@lru_cache
def get_client():
    settings = get_settings()
    return chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_port,
        settings=chromadb.config.Settings(anonymized_telemetry=False),
    )
