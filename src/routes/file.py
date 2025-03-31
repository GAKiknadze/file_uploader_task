from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, UploadFile, status
from fastapi.responses import FileResponse as FastFileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import get_db
from ..models.user import User, UserRole
from ..schemas.file import (
    FileAdminResponse,
    FileListAdminResponse,
    FileListUserResponse,
    FileResponse,
    FileUpdate,
    GetFilesListAdminRequest,
)
from ..services.auth import AccessType, AuthService
from ..services.file import FileService

router = APIRouter()


@router.get("/", response_model=FileListAdminResponse | FileListUserResponse)
async def get_files_list(
    user: User = Depends(
        AuthService.requires_role([AccessType.ADMIN, AccessType.CLIENT])
    ),
    db: AsyncSession = Depends(get_db),
    body: GetFilesListAdminRequest = Query(),
) -> FileListAdminResponse | FileListUserResponse:
    if user.role == UserRole.CLIENT:
        body.is_history = True
        body.include_deleted = False
    files, count = await FileService.get_list(
        db,
        str(user.id),
        include_deleted=body.include_deleted,
        offset=body.offset,
        limit=body.limit,
        is_history=body.is_history,
    )
    if user.role == UserRole.ADMIN:
        return FileListAdminResponse.model_validate(
            {"objects": files, "total_count": count}
        )
    else:
        return FileListUserResponse.model_validate(
            {"objects": files, "total_count": count}
        )


@router.post("/", response_model=FileAdminResponse | FileResponse)
async def upload_file(
    file: UploadFile,
    user: User = Depends(
        AuthService.requires_role([AccessType.ADMIN, AccessType.CLIENT])
    ),
    db: AsyncSession = Depends(get_db),
) -> FileAdminResponse | FileResponse:
    obj = await FileService.upload(db, user, file)

    if user.role == UserRole.ADMIN:
        return FileAdminResponse.model_validate(obj)
    else:
        return FileResponse.model_validate(obj)


@router.get("/{file_id}", response_model=FileAdminResponse | FileResponse)
async def get_file_info_by_id(
    file_id: UUID,
    user: User = Depends(
        AuthService.requires_role([AccessType.ADMIN, AccessType.CLIENT])
    ),
    db: AsyncSession = Depends(get_db),
) -> FileAdminResponse | FileResponse:
    include_deleted = False
    if user.role == UserRole.ADMIN:
        include_deleted = True
    file = await FileService.get_info_by_id(
        db, str(file_id), include_deleted=include_deleted
    )

    if user.role == UserRole.ADMIN:
        return FileAdminResponse.model_validate(file)
    else:
        return FileResponse.model_validate(file)


@router.get("/{file_id}/download", response_class=FastFileResponse)
async def download_file_by_id(
    file_id: UUID,
    user: User = Depends(
        AuthService.requires_role([AccessType.ADMIN, AccessType.CLIENT])
    ),
    db: AsyncSession = Depends(get_db),
) -> FastFileResponse:
    file = await FileService.download_by_id(db, str(file_id), user)
    return FastFileResponse(path=file.path, media_type=str(file.format))


@router.patch("/{file_id}", response_model=FileAdminResponse | FileResponse)
async def update_file_info_by_id(
    file_id: UUID,
    user: User = Depends(
        AuthService.requires_role([AccessType.ADMIN, AccessType.CLIENT])
    ),
    db: AsyncSession = Depends(get_db),
    body: FileUpdate = Body(),
) -> FileAdminResponse | FileResponse:
    file = await FileService.update_info_by_id(db, str(file_id), body, user)
    if user.role == UserRole.ADMIN:
        return FileAdminResponse.model_validate(file)
    else:
        return FileResponse.model_validate(file)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_by_id(
    file_id: UUID,
    is_hard: bool = Body(default=False),
    user: User = Depends(
        AuthService.requires_role([AccessType.ADMIN, AccessType.CLIENT])
    ),
    db: AsyncSession = Depends(get_db),
) -> None:
    if user.role == AccessType.CLIENT:
        is_hard = False
    await FileService.delete_by_id(db, str(file_id), user, is_hard=is_hard)
