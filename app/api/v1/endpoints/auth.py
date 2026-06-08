from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from services.auth_service import AuthService
from core.security import create_access_token, create_refresh_token

auth_router = APIRouter()


@auth_router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
        payload: UserRegisterRequest,
        session: AsyncSession = Depends(get_db)
        ):
    service = AuthService(session)
    user = await service.singup(email=payload.email, password=payload.password, username=payload.username)
    access_token, _ = create_access_token(user.id)
    refresh_token, _ = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest,
                session: AsyncSession = Depends(get_db)
                ):
    service = AuthService(session)
    user, access_token, refresh_token, token_type = await service.login(email=payload.email, password=payload.password)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type=token_type)