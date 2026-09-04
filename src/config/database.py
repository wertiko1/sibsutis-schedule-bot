from pydantic_settings import SettingsConfigDict

from .base import BaseConfig


class DatabaseConfig(BaseConfig):
    HOST: str = "postgres"
    PORT: int = 5432
    USER: str = "user"
    PASSWORD: str = "password"
    NAME: str = "database"

    model_config = SettingsConfigDict(env_prefix="DB_")

    def _get_url(self) -> str:
        return f"asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    def get_tortoise_config(self) -> dict:
        return {
            "connections": {"default": self._get_url()},
            "apps": {
                "models": {
                    "models": ["models"],
                    "default_connection": "default",
                    "migrations": "migrations",
                }
            },
        }
