from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import get_db
from ..schemas.auth import Token
from ..services.auth import AuthService, TokenType
from ..services.exceptions import BadRequestExc
from ..services.user import UserService
from ..services.yandex import YandexService

router = APIRouter()


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str | None = Body(default=None),
    db: AsyncSession = Depends(get_db),
) -> Token:
    token_data: dict = AuthService.verify_token(refresh_token, TokenType.REFRESH)
    user_id: str = token_data.get("sub")
    user = await UserService.get_by_id(db, user_id, include_deleted=False)
    return AuthService.create_tokens(user.id)


@router.post("/yandex")
async def oauth_yandex_login() -> RedirectResponse:
    link = await YandexService.get_auth_url()
    return RedirectResponse(link)


@router.get("/yandex/callback")
async def oauth_yandex_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    db: AsyncSession = Depends(get_db),
):
    if error:
        raise BadRequestExc(f"Yandex error: {error}")

    cookie_state = request.cookies.get("state")

    user = await YandexService.handle_callback(db, code, state, cookie_state)

    return AuthService.create_tokens(user.id)
