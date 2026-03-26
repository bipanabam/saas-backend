import os

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV = os.getenv("ENV", "dev")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f".env.{ENV}",
        env_file_encoding="utf-8",
    )

    APP_NAME: str = "Saas Backend System"
    APP_DESCRIPTION: str = (
        "A digital system where you can shape your restaurant/businesses"
    )
    API_PREFIX: str = "/api/v1"

    DEBUG: bool = False
    ENV: str = "dev"
    DATABASE_URL: str
    REDIS_URL: str


config = Settings()
