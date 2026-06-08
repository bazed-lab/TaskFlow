from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import hash_password, verify_password, create_access_token, create_refresh_token
from db.session import get_db
from models.user import User
from repositories.repositories import UserRepository
from schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse

auth_router = APIRouter()


@auth_router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
        payload: UserRegisterRequest,
        session: AsyncSession = Depends(get_db)
        ):
    pass


@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest,
                session: AsyncSession = Depends(get_db)
                ):
    pass