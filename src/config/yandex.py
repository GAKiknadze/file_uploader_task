from pydantic import BaseModel, Field


class Yandex(BaseModel):
    client_id: str = Field()
    client_secret: str = Field()
    client_uri: str = Field()
