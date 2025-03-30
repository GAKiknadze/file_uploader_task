from pydantic import BaseModel, Field


class SuperUser(BaseModel):
    login: str = Field(default="super")
    password: str = Field(default="super")


class Server(BaseModel):
    port: int = Field(8000)
    superuser: SuperUser = SuperUser()
    debug: bool = Field(default=False)
