import json
from typing import List

from pydantic import BaseModel, Field, field_validator


class File(BaseModel):
    max_size: int = Field()
    # upload_path: str = Field()
    supported_formats: list[str] = Field(default=["*"])

    @field_validator("supported_formats", mode="before")
    def parse_json(cls: "File", value: str) -> List[str]:
        if isinstance(value, str):
            return json.loads(value)
        return value
