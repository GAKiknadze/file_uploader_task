from pydantic_settings import BaseSettings, SettingsConfigDict

from .db import DB
from .file import File
from .jwt import JWT
from .server import Server
from .yandex import Yandex


class Settings(BaseSettings):
    server: Server
    jwt: JWT
    yandex: Yandex
    file: File
    db: DB

    model_config = SettingsConfigDict(
        env_nested_delimiter="_",
        env_nested_max_split=1,
        env_file=".env",
        extra="ignore",
    )


settings: Settings = Settings()
