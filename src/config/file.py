from pydantic import BaseModel, Field, field_validator
import json


class File(BaseModel):
    max_size: str = Field()
    # upload_path: str = Field()
    supported_formats: list[str] = Field(default=["*"])
    
    @field_validator("supported_formats", mode="before")
    def parse_json(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return value
