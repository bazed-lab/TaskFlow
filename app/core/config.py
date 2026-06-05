from functools import lru_cache
from pydantic import Field, BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiPrefix(BaseModel):
    prefix: str = "/api"

class Settings(BaseSettings):
    app_host: str = "127.0.0.1"
    app_port: int = 8555

    prefix: ApiPrefix = ApiPrefix()

    DATABASE_URL: str

    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = ConfigDict(env_file=".env")

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()