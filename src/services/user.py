from datetime import datetime, timezone
import logging
from sqlalchemy import delete, desc, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User, UserRole
from ..schemas.user import UserUpdate
from .exceptions import BadRequestExc, ObjectNotFoundExc, SomethingWrongExc

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    async def get_list(
        db: AsyncSession,
        include_deleted: bool = False,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[User], int]:
        query = select(User)
        query_count = select(func.count()).select_from(User)
        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))
            query_count = query_count.where(User.deleted_at.is_(None))

        query = query.order_by(desc(User.created_at))

        result = await db.execute(query.offset(offset).limit(limit))
        count = await db.execute(query_count)
        return result.scalars().all(), count.scalar_one()

    @staticmethod
    async def get_by_id(
        db: AsyncSession, user_id: str, include_deleted: bool = False
    ) -> User | None:
        query = select(User).where(User.id == user_id)
        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))

        result = await db.execute(query)
        return result.scalars().first()

    # @staticmethod
    # async def create(db: AsyncSession, user_data: UserCreate) -> User:
    #     user = User(
    #         email=user_data.email,
    #         login=user_data.login,
    #         name=user_data.name,
    #         role=UserRole.CLIENT,
    #     )

    #     try:
    #         db.add(user)
    #         await db.commit()
    #         await db.refresh(user)
    #         return user
    #     except IntegrityError as e:
    #         await db.rollback()
    #         logger.error(f"Can`t create account: {e}")
    #         if "email" in str(e):
    #             logger.debug(f"Email {user_data.email} already registered")
    #             raise BadRequestExc("Email already registered")
    #         logger.debug("User creation failed")
    #         raise BadRequestExc("User creation failed")

    @staticmethod
    async def update_by_id(
        db: AsyncSession, user_id: str, update_data: UserUpdate
    ) -> User:
        user = await UserService.get_by_id(db, user_id, include_deleted=True)
        if not user:
            logger.debug(f"User {user_id} not found")
            raise ObjectNotFoundExc("User not found")

        update_dict = update_data.dict(exclude_unset=True)

        await db.execute(update(User).where(User.id == user_id).values(**update_dict))
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete_by_id(
        db: AsyncSession, user_id: str, is_hard: bool = False
    ) -> None:
        user = await UserService.get_by_id(db, user_id, include_deleted=True)
        if not user:
            logger.debug(f"User {user_id} not found")
            raise ObjectNotFoundExc("User not found")

        if is_hard:
            await db.execute(delete(User).where(User.id == user_id))
        else:
            user.deleted_at = datetime.now(timezone.utc)

        try:
            await db.commit()
            if not is_hard:
                await db.refresh(user)
        except Exception as e:
            await db.rollback()
            logger.warning(f"Deletion failed: {str(e)}")
            raise SomethingWrongExc("Deletion failed")

    @staticmethod
    async def restore_by_id(db: AsyncSession, user_id: str) -> User:
        user = await UserService.get_by_id(db, user_id, include_deleted=True)
        if not user:
            logger.debug(f"User {user_id} not found")
            raise ObjectNotFoundExc("User not found")

        if not user.deleted_at:
            logger.debug(f"User {user_id} is not deleted")
            raise BadRequestExc("User is not deleted")

        user.deleted_at = None
        await db.commit()
        await db.refresh(user)
        return user
