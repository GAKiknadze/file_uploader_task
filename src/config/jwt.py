from pydantic import BaseModel, Field


class JWT(BaseModel):
    secret_key: str = Field()
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_minutes: int = Field(default=7)
