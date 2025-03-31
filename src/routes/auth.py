from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import get_db
from ..schemas.auth import Token
from ..services.auth import AuthService, TokenType
from ..services.exceptions import BadRequestExc, ObjectNotFoundExc
from ..services.user import UserService
from ..services.yandex import YandexService

router = APIRouter()


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str | None = Body(default=None, embed=True),
    db: AsyncSession = Depends(get_db),
) -> Token:
    token_data = AuthService.verify_token(refresh_token, TokenType.REFRESH)
    user_id = token_data.get("sub")
    user = await UserService.get_by_id(db, str(user_id), include_deleted=False)
    if user is None:
        raise ObjectNotFoundExc(f"User {user_id} is not found")
    return AuthService.create_tokens(str(user.id))


@router.post("/yandex")
async def oauth_yandex_login() -> RedirectResponse:
    link = await YandexService.get_auth_url()
    return RedirectResponse(link)


@router.get("/yandex/callback")
async def oauth_yandex_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    if error or state is None or code is None:
        raise BadRequestExc(f"Yandex error: {error}")

    cookie_state = request.cookies.get("state")

    user = await YandexService.handle_callback(db, code, state, cookie_state)

    return AuthService.create_tokens(str(user.id))
