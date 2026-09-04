from pydantic import field_validator
from pydantic_settings import SettingsConfigDict

from .base import BaseConfig


class BotConfig(BaseConfig):
    TOKEN: str
    ADMIN_IDS: list[int] = []

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: object) -> list[int]:
        if isinstance(v, str):
            return [int(x) for x in v.strip("[] ").split(",") if x.strip()]
        return v  # type: ignore[return-value]

    model_config = SettingsConfigDict(env_prefix="BOT_")
