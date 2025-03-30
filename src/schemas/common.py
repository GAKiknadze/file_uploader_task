from pydantic import BaseModel, Field


class ObjectListRequest(BaseModel):
    limit: int = Field(default=50, gt=0, le=200)
    offset: int = Field(default=0, ge=0)


class ObjectListAdminFilters(BaseModel):
    include_deleted: bool = Field(default=False)
