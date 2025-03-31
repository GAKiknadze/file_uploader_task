import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models.file import File
from ..models.user import User, UserRole
from ..schemas.file import FileUpdate
from .exceptions import (
    AccessDeniedExc,
    BadRequestExc,
    ObjectNotFoundExc,
    SomethingWrongExc,
)

logger = logging.getLogger(__name__)


class FileService:
    @staticmethod
    async def get_list(
        db: AsyncSession,
        user_id: str,
        include_deleted: bool = False,
        offset: int = 0,
        limit: int = 100,
        is_history: bool = True,
    ) -> List[File]:
        query = select(File)
        query_count = select(func.count()).select_from(File)

        if is_history:
            query = query.where(File.user_id == user_id)
            query_count = query_count.where(File.user_id == user_id)

        if not include_deleted:
            query = query.where(File.deleted_at.is_(None))
            query_count = query_count.where(File.deleted_at.is_(None))

        query = query.order_by(desc(File.created_at))

        result = await db.execute(query.offset(offset).limit(limit))
        count = await db.execute(query_count)
        return result.scalars().all(), count.scalar_one()

    @staticmethod
    async def get_info_by_id(
        db: AsyncSession, file_id: str, include_deleted: bool = False
    ) -> Optional[File]:
        query = select(File).where(File.id == file_id)
        if not include_deleted:
            query = query.where(File.deleted_at.is_(None))

        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def download_by_id(db: AsyncSession, file_id: str, user: User) -> File:
        file = await FileService.get_info_by_id(db, file_id)
        if not file:
            logger.debug(f"File {file_id} not found")
            raise ObjectNotFoundExc("File not found")

        if file.user_id != user.id and user.role != UserRole.ADMIN:
            logger.debug(f"File {file_id} access denied")
            raise AccessDeniedExc("Access denied")

        file_path = Path(file.path)
        if not file_path.exists():
            logger.debug(f"File {file_id} not found on disk")
            raise ObjectNotFoundExc("File not found on disk")

        return file

    @staticmethod
    async def upload(
        db: AsyncSession, user: User, upload_file: UploadFile
    ) -> File | None:
        if (
            "*" not in settings.file.supported_formats
            and upload_file.content_type not in settings.file.supported_formats
        ):
            logger.debug(f"Invalid file type: {upload_file.content_type}")
            raise BadRequestExc("Invalid file type")

        user_dir = Path("/uploads") / str(user.id)
        user_dir.mkdir(exist_ok=True, parents=True)

        file_ext = upload_file.filename.split(".")[-1]
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.{file_ext}"
        file_path = user_dir / filename
        temp_path = file_path.with_suffix(".tmp")

        new_file: File = None

        try:
            file_size = 0
            with open(temp_path, "wb") as buffer:
                while chunk := await upload_file.read(1024 * 1024):
                    file_size += len(chunk)
                    if file_size > settings.file.max_size * 1024 * 1024:
                        logger.debug(f"File {file_id} too large")
                        raise BadRequestExc("File too large")
                    buffer.write(chunk)

            temp_path.rename(file_path)

            new_file = File(
                id=file_id,
                user_id=user.id,
                filename=upload_file.filename,
                size=file_size,
                format=upload_file.content_type.split("/")[-1],
                path=str(file_path),
            )

            db.add(new_file)
            await db.commit()
            await db.refresh(new_file)

        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            if file_path.exists():
                file_path.unlink()
            logger.warning(f"File upload failed: {str(e)}")
            raise SomethingWrongExc("File upload failed")
        finally:
            await upload_file.close()
        return new_file

    @staticmethod
    async def update_info_by_id(
        db: AsyncSession, file_id: str, update_data: FileUpdate, user: User
    ) -> File:
        file = await FileService.get_info_by_id(db, file_id)
        if not file:
            logger.debug(f"File {file_id} not found")
            raise ObjectNotFoundExc("File not found")

        if file.user_id != user.id and user.role != UserRole.ADMIN:
            logger.debug(f"File {file_id} access denied")
            raise AccessDeniedExc("Access denied")

        update_dict = update_data.model_dump(exclude_unset=True)
        if "filename" in update_dict:
            new_filename = update_dict["filename"]
            old_path = Path(file.path)
            new_path = old_path.with_name(new_filename)

            try:
                old_path.rename(new_path)
                file.path = str(new_path)
                file.filename = new_filename
            except OSError as e:
                logger.warning(f"File rename failed: {str(e)}")
                raise SomethingWrongExc("File rename failed")

        await db.commit()
        await db.refresh(file)
        return file

    @staticmethod
    async def delete_by_id(
        db: AsyncSession, file_id: str, user: User, is_hard: bool = False
    ) -> None:
        file = await FileService.get_info_by_id(db, file_id, include_deleted=True)
        if not file:
            logger.debug(f"File {file_id} not found")
            raise ObjectNotFoundExc("File not found")

        if file.user_id != user.id and user.role != UserRole.ADMIN:
            logger.debug(f"File {file_id} access denied")
            raise AccessDeniedExc("Access denied")

        if is_hard:
            try:
                Path(file.path).unlink()
            except FileNotFoundError:
                pass
            await db.delete(file)
        else:
            file.deleted_at = datetime.utcnow()

        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.warning(f"Deletion failed: {str(e)}")
            raise SomethingWrongExc("Deletion failed")

    @staticmethod
    async def restore_by_id(db: AsyncSession, file_id: str, user: User) -> File:
        file = await FileService.get_info_by_id(db, file_id, include_deleted=True)
        if not file:
            logger.debug(f"File {file_id} not found")
            raise ObjectNotFoundExc("File not found")

        if file.user_id != user.id and user.role != UserRole.ADMIN:
            logger.debug(f"File {file_id} access denied")
            raise AccessDeniedExc("Access denied")

        if not file.deleted_at:
            logger.debug(f"File {file_id} is not deleted")
            raise BadRequestExc("File is not deleted")

        file.deleted_at = None
        await db.commit()
        await db.refresh(file)
        return file
