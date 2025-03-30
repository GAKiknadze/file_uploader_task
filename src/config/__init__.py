from pydantic_settings import BaseSettings, SettingsConfigDict

from .db import DB
from .file import File
from .jwt import JWT
from .server import Server
from .yandex import Yandex


class Settings(BaseSettings):
    model_config = SettingsConfigDict()
    server: Server = Server()
    jwt: JWT = JWT()
    yandex: Yandex = Yandex()
    file: File = File()
    db: DB = DB()


settings = Settings()
