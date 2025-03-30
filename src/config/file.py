from pydantic import BaseModel, Field


class File(BaseModel):
    max_size: str = Field()
    upload_path: str = Field()
    supported_formats: list[str] = Field()
