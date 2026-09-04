from pydantic_settings import SettingsConfigDict

from .base import BaseConfig


class SibsutisConfig(BaseConfig):
    LOGIN: str = "user"
    PASSWORD: str = "password"

    model_config = SettingsConfigDict(env_prefix="SIBSUTIS_")
