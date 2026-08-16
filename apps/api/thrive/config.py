from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite:///./thrive.db"
    web_origin: str = "http://localhost:3000"
    news_api_key: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def settings() -> Settings:
    return Settings()
