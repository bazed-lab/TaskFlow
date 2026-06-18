from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.repositories import ProjectRepository, UserRepository


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.project_repo = ProjectRepository(session)
        self.user_repo = UserRepository(session)

    async def check_admin(self, project_id: str, user_id: int):
        member = await self.project_repo.get_member(project_id, user_id)
        if not member or member.role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can do this")

    async def create_project(self, name: str, description: str | None, secret_key: str | None, owner_id: int):
        project = await self.project_repo.create(
            name=name, description=description, secret_key=secret_key, owner_id=owner_id,
        )
        await self.project_repo.add_member(project_id=project.id, user_id=owner_id, role="admin")
        return project

    async def get_user_projects(self, user_id: int):
        return await self.project_repo.get_member_projects(user_id)

    async def get_project(self, project_id: str, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        member = await self.project_repo.get_member(project_id, user_id)
        if not member:
            raise HTTPException(status_code=403, detail="Access denied")
        members = await self.project_repo.get_members(project_id)
        return project, members

    async def join_project(self, invite: str, user_id: int):
        try:
            project_id, secret_key = invite.split("/", 1)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid invite format")

        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if not project.secret_key:
            raise HTTPException(status_code=400, detail="This project does not have an invite link")
        if project.secret_key != secret_key:
            raise HTTPException(status_code=403, detail="Invalid secret key")

        existing = await self.project_repo.get_member(project_id, user_id)
        if existing:
            raise HTTPException(status_code=400, detail="You are already a member")

        member = await self.project_repo.add_member(project_id=project_id, user_id=user_id, role="member")
        return await self._enrich_member(member)

    async def _enrich_member(self, member):
        user = await self.user_repo.get_by_id(member.user_id)
        return {
            "id": member.id,
            "user_id": member.user_id,
            "role": member.role,
            "username": user.username if user else "Unknown",
            "handle": user.handle if user else "@unknown",
        }

    async def add_member(self, project_id: str, current_user_id: int, handle: str, role: str = "member"):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await self.check_admin(project_id, current_user_id)
        user = await self.user_repo.get_by_handle(handle)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        existing = await self.project_repo.get_member(project_id, user.id)
        if existing:
            raise HTTPException(status_code=400, detail="User already a member")
        member = await self.project_repo.add_member(project_id=project_id, user_id=user.id, role=role)
        return await self._enrich_member(member)

    async def update_member_role(self, project_id: str, current_user_id: int, target_user_id: int, role: str):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await self.check_admin(project_id, current_user_id)
        member = await self.project_repo.get_member(project_id, target_user_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        member = await self.project_repo.update_member_role(project_id, target_user_id, role)
        return await self._enrich_member(member)

    async def remove_member(self, project_id: str, current_user_id: int, target_user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await self.check_admin(project_id, current_user_id)
        member = await self.project_repo.get_member(project_id, target_user_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        if target_user_id == project.owner_id:
            raise HTTPException(status_code=400, detail="Cannot remove the project owner")
        await self.project_repo.remove_member(project_id, target_user_id)
