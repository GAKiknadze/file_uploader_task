from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List

from fastapi import Depends, Header
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from ..config import settings
from ..models.base import get_db
from ..models.user import User, UserRole
from ..schemas.auth import Token
from ..services.exceptions import AccessDeniedExc, NotAuthorizedExc
from ..services.user import UserService

INVALID_EXC = NotAuthorizedExc("Invalid token")


class AccessType(str, Enum):
    ADMIN = "ADMIN"
    CLIENT = "CLIENT"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class AuthService:
    @staticmethod
    def create_tokens(user_id: str) -> Token:
        user_id = str(user_id)
        return Token(
            access_token=AuthService._create_token(
                user_id, settings.jwt.access_token_expire_minutes, TokenType.ACCESS
            ),
            refresh_token=AuthService._create_token(
                user_id,
                settings.jwt.refresh_token_expire_days * 1440,
                TokenType.REFRESH,
            ),
        )

    @staticmethod
    def _create_token(user_id: str, expires_minutes: int, type_: TokenType) -> str:
        expire = datetime.now() + timedelta(minutes=expires_minutes)
        return jwt.encode(
            {"sub": str(user_id), "exp": expire, "type": type_},
            settings.jwt.secret_key,
            algorithm=settings.jwt.algorithm,
        )

    @staticmethod
    async def get_or_create_user(db: AsyncSession, yandex_data: Dict[str, Any]) -> User:
        result = await db.execute(
            select(User).where(User.yandex_id == yandex_data["id"])
        )
        user = result.scalars().first()

        if user is None:
            user = User(
                yandex_id=yandex_data["id"],
                email=yandex_data.get("default_email"),
                login=yandex_data["login"],
                name=yandex_data.get("real_name"),
                role=UserRole.CLIENT,
            )
            db.add(user)
            await db.commit()

        return user

    @staticmethod
    def verify_token(token: str | None, type_: TokenType) -> Dict[str, Any]:
        try:
            if token is None:
                raise JWTError()
            data = jwt.decode(
                token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm]
            )
            if data.get("type") != type_:
                raise JWTError()
            return data
        except JWTError:
            raise INVALID_EXC

    @staticmethod
    async def get_user_from_token(
        authorization: str | None = Header(None), db: AsyncSession = Depends(get_db)
    ) -> User | None:
        if not authorization:
            raise INVALID_EXC

        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise INVALID_EXC
        except ValueError:
            raise INVALID_EXC

        payload = AuthService.verify_token(token, TokenType.ACCESS)

        user_id = payload.get("sub")
        if not user_id:
            raise INVALID_EXC

        user = await UserService.get_by_id(db, user_id)
        if user is None:
            raise INVALID_EXC

        if user.deleted_at is not None or user.is_active is False:
            raise INVALID_EXC

        return user

    @staticmethod
    def requires_role(required_roles: List[AccessType]) -> Callable[[User], User]:
        def checker(user: User = Depends(AuthService.get_user_from_token)) -> User:
            if user is None or user.role not in required_roles:
                raise AccessDeniedExc("Insufficient permissions")
            return user

        return checker
