from pydantic import BaseModel, Field, PostgresDsn


class DB(BaseModel):
    uri: PostgresDsn = Field()
    pool_size: int = Field(default=20)
    max_overflow: int = Field(default=10)
