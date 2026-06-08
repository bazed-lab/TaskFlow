from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
            self, user_id: int
    ):
        return await self.session.scalar(select(User).where(User.id == user_id))

    async def get_by_email(self, email: str):
        return await self.session.scalar(select(User).where(User.email == email))

    async def get_by_username(self, username: str):
        return await self.session.scalar(select(User).where(User.username == username))

    async def create(self, **kwargs):
        user = User(**kwargs)
        self.session.add(user)
        await self.session.flush()
        return user
