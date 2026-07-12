from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # API gateway - shared secret also checked by Nginx (see nginx/templates/)
    api_key: str = "changeme-generate-a-real-secret"

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

    # Manager identity mapping (login page, no auth/passwords)
    manager_england: str = ""
    manager_france: str = ""
    manager_brazil: str = ""
    manager_argentina: str = ""
    manager_spain: str = ""
    manager_germany: str = ""
    manager_portugal: str = ""

    @property
    def team_list(self) -> list[str]:
        return [t.strip() for t in self.teams.split(",") if t.strip()]

    @property
    def managers(self) -> dict:
        return {
            "england": self.manager_england,
            "france": self.manager_france,
            "brazil": self.manager_brazil,
            "argentina": self.manager_argentina,
            "spain": self.manager_spain,
            "germany": self.manager_germany,
            "portugal": self.manager_portugal,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
