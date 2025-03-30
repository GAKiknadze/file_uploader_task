from pydantic import BaseModel, Field

class Server(BaseModel):
    debug: bool = Field(default=False)
