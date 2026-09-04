from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)

_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
    )
