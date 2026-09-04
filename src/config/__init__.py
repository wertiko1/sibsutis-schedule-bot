from functools import lru_cache

from aiogram.types import BotCommand
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from .base import BaseConfig
from .bot import BotConfig
from .commands import COMMANDS
from .database import DatabaseConfig
from .sibsutis import SibsutisConfig


class Settings(BaseConfig):
    bot: BotConfig = Field(default_factory=BotConfig)
    sibsutis: SibsutisConfig = Field(default_factory=SibsutisConfig)
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    commands: list[BotCommand] = COMMANDS

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
