from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from jose import JWTError

from repositories.repositories import UserRepository
from core.security import create_access_token, create_refresh_token, decode_refresh_token, hash_password, verify_password


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)

    async def singup(self, email: str, password: str, username: str, handle: str):
        if await self.users.get_by_email(email):
            raise HTTPException(status_code=400, detail="Email already registered")
        if await self.users.get_by_username(username):
            raise HTTPException(status_code=400, detail="Username already registered")
        if await self.users.get_by_handle(handle):
            raise HTTPException(status_code=400, detail="Handle already taken")
        user = await self.users.create(
            email=email,
            username=username,
            handle=handle,
            password_hash=hash_password(password),
        )
        return user

    async def login(self, email: str, password: str):
        user = await self.users.get_by_email(email)
        if not user:
            raise HTTPException(status_code=400, detail="Email not registered")
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is disabled")
        access_token, _ = create_access_token(user.id)
        refresh_token, _ = create_refresh_token(user.id)
        return user, access_token, refresh_token, "bearer"

    async def refresh(self, refresh_token: str):
        try:
            payload = decode_refresh_token(refresh_token)
        except (JWTError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

        user_id = int(payload["sub"])
        user = await self.users.get_by_id(user_id)

        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is disabled")

        new_refresh, _ = create_refresh_token(user.id)
        return new_refresh
    