from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .common import ObjectListAdminFilters, ObjectListRequest


class FileBase(BaseModel):
    filename: str = Field(..., max_length=255, example="my_song.mp3")
    format: str = Field(..., max_length=10, example="mp3")


class FileUpdate(BaseModel):
    filename: Optional[str] = Field(None, max_length=255, example="new_filename.mp3")


class FileResponse(FileBase):
    id: UUID
    size: int
    path: str
    created_at: datetime

    class Config:
        orm_mode = True


class FileAdminResponse(FileResponse):
    deleted_at: Optional[datetime]
    user_id: UUID

    class Config:
        orm_mode = True


class FileListUserResponse(BaseModel):
    objects: list[FileResponse]
    total_count: int


class FileListAdminResponse(BaseModel):
    objects: list[FileAdminResponse]
    total_count: int


class GetFilesListUserRequest(ObjectListRequest):
    pass


class GetFilesListAdminRequest(ObjectListAdminFilters, GetFilesListUserRequest):
    is_history: bool = Field(default=False)
