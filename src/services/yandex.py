import logging
import uuid

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models.user import User
from .auth import AuthService
from .exceptions import BadRequestExc

logger = logging.getLogger(__name__)


class YandexService:
    OAUTH_URL = "https://oauth.yandex.ru/authorize"
    TOKEN_URL = "https://oauth.yandex.ru/token"
    USER_INFO_URL = "https://login.yandex.ru/info"

    @staticmethod
    async def get_auth_url() -> str:
        state = str(uuid.uuid4())
        params = {
            "response_type": "code",
            "client_id": settings.yandex.client_id,
            "redirect_uri": settings.yandex.client_uri,
            "scope": "login:info",
            "state": state,
        }
        return f"{YandexService.OAUTH_URL}?{httpx.QueryParams(params)}"

    @staticmethod
    async def handle_callback(
        db: AsyncSession, code: str, state: str, cookie_state: str
    ) -> User:
        if state != cookie_state:
            logger.error("Invalid state parameter")
            raise BadRequestExc("Invalid state parameter")

        token_data = await YandexService._get_access_token(code)

        user_info = await YandexService._get_user_info(token_data["access_token"])

        return await AuthService.get_or_create_user(db, user_info)

    @staticmethod
    async def _get_access_token(code: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    YandexService.TOKEN_URL,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "client_id": settings.yandex_client_id,
                        "client_secret": settings.yandex_client_secret,
                        "redirect_uri": settings.yandex_redirect_uri,
                    },
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Yandex token error: {e.response.text}")
            raise BadRequestExc("Failed to get access token from Yandex")

    @staticmethod
    async def _get_user_info(access_token: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    YandexService.USER_INFO_URL,
                    headers={"Authorization": f"OAuth {access_token}"},
                    params={"format": "json"},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Yandex user info error: {e.response.text}")
            raise BadRequestExc("Failed to get user info from Yandex")
