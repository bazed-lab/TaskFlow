from functools import lru_cache
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiPrefix(BaseModel):
    prefix: str = "/api"

class Settings(BaseSettings):
    app_host: str = "127.0.0.1"
    app_port: int = 8555

    prefix: ApiPrefix = ApiPrefix()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()