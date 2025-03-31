from pydantic import BaseModel, Field


class DB(BaseModel):
    uri: str = Field()
    pool_size: int = Field(default=20)
    max_overflow: int = Field(default=10)
