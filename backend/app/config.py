from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ClickHouse
    clickhouse_host: str = "clickhouse"
    clickhouse_port: int = 8123
    clickhouse_user: str = "default"
    clickhouse_password: str = "changeme"
    clickhouse_master_db: str = "squad_data_store"

    # ChromaDB (unused until the RAG phase)
    chroma_host: str = "chroma"
    chroma_port: int = 8000

    # LLM provider (unused until a key is added)
    llm_provider: str = "anthropic"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_model: str = ""

    # External data APIs (unused until the ingestion phase)
    api_football_key: str = ""
    thesportsdb_key: str = "3"
    newsapi_key: str = ""
    transfermarkt_api_base: str = "http://transfermarkt-api:8000"

    # App config
    teams: str = "england,france,brazil,argentina,spain,germany,portugal"
    ingestion_interval_hours: int = 6
    chart_output_dir: str = "/app/charts"

    @property
    def team_list(self) -> list[str]:
        return [t.strip() for t in self.teams.split(",") if t.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
