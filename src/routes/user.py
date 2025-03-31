from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import get_db
from ..models.user import User, UserRole
from ..schemas.user import (
    GetUsersListAdminRequest,
    UserAdminResponse,
    UserResponse,
    UsersListAdminResponse,
    UserUpdate,
    UserUpdateAdminRequest,
)
from ..services.auth import AccessType, AuthService
from ..services.exceptions import ObjectNotFoundExc
from ..services.user import UserService

router = APIRouter()


@router.get("/", response_model=UsersListAdminResponse)
async def get_users_list(
    _: User = Depends(AuthService.requires_role([AccessType.ADMIN])),
    db: AsyncSession = Depends(get_db),
    filters: GetUsersListAdminRequest = Query(),
) -> tuple[list[User], int]:
    return await UserService.get_list(
        db,
        include_deleted=filters.include_deleted,
        offset=filters.offset,
        limit=filters.limit,
    )


@router.get("/{user_id}", response_model=UserAdminResponse)
async def get_user_by_id(
    user_id: UUID,
    _: User = Depends(AuthService.requires_role([AccessType.ADMIN])),
    db: AsyncSession = Depends(get_db),
) -> User:
    obj = await UserService.get_by_id(db, str(user_id), include_deleted=True)
    if obj is None:
        raise ObjectNotFoundExc(f"User with id {user_id} not found")
    return obj


@router.patch("/{user_id}", response_model=UserAdminResponse)
async def update_user_by_id(
    user_id: UUID,
    _: User = Depends(AuthService.requires_role([AccessType.ADMIN])),
    db: AsyncSession = Depends(get_db),
    data: UserUpdateAdminRequest = Body(),
) -> User:
    return await UserService.update_by_id(db, str(user_id), data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: UUID,
    is_hard: bool,
    _: User = Depends(AuthService.requires_role([AccessType.ADMIN])),
    db: AsyncSession = Depends(get_db),
) -> None:
    await UserService.delete_by_id(db, str(user_id), is_hard=is_hard)


@router.post("/{user_id}/restore", response_model=UserAdminResponse)
async def restore_user_by_id(
    user_id: UUID,
    _: User = Depends(AuthService.requires_role([AccessType.ADMIN])),
    db: AsyncSession = Depends(get_db),
) -> User:
    return await UserService.restore_by_id(db, str(user_id))


@router.get("/me", response_model=UserAdminResponse | UserResponse)
async def get_my_info(
    user: User = Depends(
        AuthService.requires_role([AccessType.ADMIN, AccessType.CLIENT])
    ),
) -> UserAdminResponse | UserResponse:
    if user.role == UserRole.ADMIN:
        return UserAdminResponse.model_validate(user)
    else:
        return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserAdminResponse | UserResponse)
async def update_my_info(
    user: User = Depends(
        AuthService.requires_role([AccessType.ADMIN, AccessType.CLIENT])
    ),
    db: AsyncSession = Depends(get_db),
    data: UserUpdate = Body(),
) -> UserAdminResponse | UserResponse:
    obj = await UserService.update_by_id(db, str(user.id), data)
    if user.role == UserRole.ADMIN:
        return UserAdminResponse.model_validate(obj)
    else:
        return UserResponse.model_validate(obj)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_info(
    user: User = Depends(
        AuthService.requires_role([AccessType.ADMIN, AccessType.CLIENT])
    ),
    db: AsyncSession = Depends(get_db),
) -> None:
    await UserService.delete_by_id(db, str(user.id), is_hard=False)
