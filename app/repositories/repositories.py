from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.project import Project, ProjectMember


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

    async def get_by_handle(self, handle: str):
        return await self.session.scalar(select(User).where(User.handle == handle))

    async def create(self, **kwargs):
        user = User(**kwargs)
        self.session.add(user)
        await self.session.flush()
        return user


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, project_id: str):
        return await self.session.scalar(select(Project).where(Project.id == project_id))

    async def get_by_owner_id(self, owner_id: int):
        result = await self.session.scalars(select(Project).where(Project.owner_id == owner_id))
        return result.all()

    async def get_member_projects(self, user_id: int):
        result = await self.session.scalars(
            select(Project).join(ProjectMember).where(ProjectMember.user_id == user_id)
        )
        return result.all()

    async def create(self, **kwargs):
        project = Project(**kwargs)
        self.session.add(project)
        await self.session.flush()
        return project

    async def add_member(self, project_id: str, user_id: int, role: str = "member"):
        member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
        self.session.add(member)
        await self.session.flush()
        return member

    async def get_member(self, project_id: str, user_id: int):
        return await self.session.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )

    async def get_members(self, project_id: str):
        result = await self.session.execute(
            select(ProjectMember.id, ProjectMember.user_id, ProjectMember.role, User.username, User.handle)
            .join(User, ProjectMember.user_id == User.id)
            .where(ProjectMember.project_id == project_id)
        )
        rows = result.all()
        return [
            {"id": row.id, "user_id": row.user_id, "role": row.role, "username": row.username, "handle": row.handle}
            for row in rows
        ]

    async def update_member_role(self, project_id: str, user_id: int, role: str):
        member = await self.get_member(project_id, user_id)
        if member:
            member.role = role
            await self.session.flush()
        return member

    async def remove_member(self, project_id: str, user_id: int):
        await self.session.execute(
            delete(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        await self.session.flush()
