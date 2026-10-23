from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
    )
    app_name: str
    database_url: str
    redis_url: str
    secret_key: str
    debug: bool
    algorithm: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30


settings = Settings()
