from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, MessageResponse
from services.auth_service import AuthService
from core.security import create_access_token, create_refresh_token
from core.config import get_settings

auth_router = APIRouter()


@auth_router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def signup(
        payload: UserRegisterRequest,
        session: AsyncSession = Depends(get_db)
        ):
    service = AuthService(session)
    await service.singup(email=payload.email, password=payload.password, username=payload.username)
    return MessageResponse(message="Вы зарегистрировались")


@auth_router.post("/login", response_model=TokenResponse)
async def login(
        payload: UserLoginRequest,
        response: Response,
        session: AsyncSession = Depends(get_db)
        ):
    service = AuthService(session)
    user, access_token, refresh_token, token_type = await service.login(email=payload.email, password=payload.password)
    settings = get_settings()
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        samesite="lax",
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type=token_type)