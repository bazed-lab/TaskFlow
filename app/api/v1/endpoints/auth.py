from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from schemas.auth import (
    UserRegisterRequest, UserLoginRequest, TokenResponse,
    MessageResponse, RefreshTokenRequest, UserUpdateRequest, UserResponse,
)
from services.auth_service import AuthService
from core.security import create_access_token, decode_refresh_token, decode_access_token, hash_password
from core.config import get_settings
from repositories.repositories import UserRepository

auth_router = APIRouter()
users_router = APIRouter()

_refresh_blacklist: set[str] = set()
http_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_db),
):
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(payload["sub"])
    user = await UserRepository(session).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    return user


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


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(
        request: Request,
        response: Response,
        session: AsyncSession = Depends(get_db)
        ):
    refresh_token_cookie = request.cookies.get("refresh_token")
    if not refresh_token_cookie:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    service = AuthService(session)
    new_refresh_token = await service.refresh(refresh_token=refresh_token_cookie)
    payload_data = decode_refresh_token(new_refresh_token)
    access_token, _ = create_access_token(int(payload_data["sub"]))
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
        value=new_refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        samesite="lax",
    )
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token, token_type="bearer")

@auth_router.post("/logout", response_model=MessageResponse)
async def logout(
        payload: RefreshTokenRequest,
        current_user = Depends(get_current_user),
):
    _refresh_blacklist.add(payload.refresh_token)
    return MessageResponse(message="Logged out successfully")


@users_router.get("/me", response_model=UserResponse)
async def get_me(
        current_user = Depends(get_current_user),
):
    return current_user


@users_router.patch("/me", response_model=UserResponse)
async def update_me(
        payload: UserUpdateRequest,
        current_user = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),
):
    repo = UserRepository(session)

    if payload.username is not None:
        existing = await repo.get_by_username(payload.username)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = payload.username

    if payload.email is not None and payload.email != current_user.email:
        existing = await repo.get_by_email(payload.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = payload.email

    if payload.password is not None:
        current_user.password_hash = hash_password(payload.password)

    await session.flush()
    await session.refresh(current_user)
    return current_user
