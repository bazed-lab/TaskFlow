from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from schemas.auth import (
    UserRegisterRequest, UserLoginRequest, TokenResponse,
    MessageResponse, RefreshTokenRequest, UserUpdateRequest, UserResponse,
)
from services.auth_service import AuthService
from core.security import create_access_token, decode_refresh_token, decode_access_token, hash_password, verify_password
from core.config import get_settings
from repositories.repositories import UserRepository

auth_router = APIRouter()
users_router = APIRouter()

_refresh_blacklist: set[str] = set()


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    token = None

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_access_token(token)
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


@auth_router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="Регистрация")
async def signup(
        payload: UserRegisterRequest,
        session: AsyncSession = Depends(get_db)
        ):
    """Создаёт нового пользователя с email, username и паролем."""
    service = AuthService(session)
    await service.singup(email=payload.email, password=payload.password, username=payload.username)
    return MessageResponse(message="Вы зарегистрировались")


@auth_router.post("/login", response_model=TokenResponse, summary="Вход")
async def login(
        payload: UserLoginRequest,
        response: Response,
        session: AsyncSession = Depends(get_db)
        ):
    """Аутентификация пользователя. Возвращает access и refresh токены."""
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


@auth_router.post("/refresh", response_model=TokenResponse, summary="Обновить токены")
async def refresh(
        request: Request,
        response: Response,
        session: AsyncSession = Depends(get_db)
        ):
    """Обновляет access и refresh токены по refresh_token из куки."""
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

@auth_router.post("/logout", response_model=MessageResponse, summary="Выход")
async def logout(
        payload: RefreshTokenRequest,
        current_user = Depends(get_current_user),
):
    """Инвалидирует refresh токен. Требуется access_token."""
    _refresh_blacklist.add(payload.refresh_token)
    return MessageResponse(message="Logged out successfully")


@users_router.get("/me", response_model=UserResponse, summary="Профиль")
async def get_me(
        current_user = Depends(get_current_user),
):
    """Возвращает информацию о текущем пользователе."""
    return current_user


@users_router.patch("/me", response_model=UserResponse, summary="Обновить профиль")
async def update_me(
        payload: UserUpdateRequest,
        current_user = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),
    ):
    """Обновляет username, email или пароль текущего пользователя."""
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
        if payload.old_password is None:
            raise HTTPException(status_code=400, detail="Old password is required to set a new password")
        if not verify_password(payload.old_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="Old password is incorrect")
        current_user.password_hash = hash_password(payload.password)

    await session.flush()
    await session.refresh(current_user)
    return current_user
