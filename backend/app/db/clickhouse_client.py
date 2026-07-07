from functools import lru_cache

import clickhouse_connect
from clickhouse_connect.driver.client import Client

from app.config import get_settings


@lru_cache
def get_client() -> Client:
    settings = get_settings()
    return clickhouse_connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password,
    )
