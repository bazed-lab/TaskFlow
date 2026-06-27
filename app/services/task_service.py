from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.repositories import TaskRepository, ProjectRepository


class TaskService:
    def __init__(self, session: AsyncSession):
        self.task_repo = TaskRepository(session)
        self.project_repo = ProjectRepository(session)

    async def _check_project_member(self, project_id: str, user_id: int):
        member = await self.project_repo.get_member(project_id, user_id)
        if not member:
            raise HTTPException(status_code=403, detail="Access denied")

    async def _check_admin(self, project_id: str, user_id: int):
        member = await self.project_repo.get_member(project_id, user_id)
        if not member or member.role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can do this")

    async def create_task(self, project_id: str, user_id: int, title: str, description: str | None,
                          assigned_to: int | None, priority: str, deadline: datetime | None = None):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await self._check_admin(project_id, user_id)

        if assigned_to:
            assignee = await self.project_repo.get_member(project_id, assigned_to)
            if not assignee:
                raise HTTPException(status_code=400, detail="Assignee is not a member of this project")

        task = await self.task_repo.create(
            project_id=project_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            created_by=user_id,
            priority=priority,
            deadline=deadline,
        )
        return task

    async def get_tasks(self, project_id: str, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await self._check_project_member(project_id, user_id)
        return await self.task_repo.get_by_project(project_id)

    async def get_task(self, project_id: str, task_id: int, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await self._check_project_member(project_id, user_id)

        task = await self.task_repo.get_by_id(task_id)
        if not task or task.project_id != project_id:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    async def update_task(self, project_id: str, task_id: int, user_id: int, **kwargs):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        task = await self.task_repo.get_by_id(task_id)
        if not task or task.project_id != project_id:
            raise HTTPException(status_code=404, detail="Task not found")

        member = await self.project_repo.get_member(project_id, user_id)
        if not member:
            raise HTTPException(status_code=403, detail="Access denied")

        is_admin = member.role == "admin"
        is_assignee = task.assigned_to == user_id

        if not is_admin and not is_assignee:
            raise HTTPException(status_code=403, detail="Only admin or assignee can update this task")

        if not is_admin:
            allowed = {"status"}
            extra = set(kwargs.keys()) - allowed
            if extra:
                raise HTTPException(status_code=403, detail=f"Only admin can change: {', '.join(extra)}")

        if kwargs.get("assigned_to"):
            assignee = await self.project_repo.get_member(project_id, kwargs["assigned_to"])
            if not assignee:
                raise HTTPException(status_code=400, detail="Assignee is not a member of this project")

        task = await self.task_repo.update(task, **kwargs)
        return task

    async def complete_task(self, project_id: str, task_id: int, user_id: int, comment: str | None = None):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        task = await self.task_repo.get_by_id(task_id)
        if not task or task.project_id != project_id:
            raise HTTPException(status_code=404, detail="Task not found")

        member = await self.project_repo.get_member(project_id, user_id)
        if not member:
            raise HTTPException(status_code=403, detail="Access denied")

        if task.assigned_to != user_id:
            raise HTTPException(status_code=403, detail="Only the assignee can complete this task")

        task = await self.task_repo.update(
            task,
            status="done",
            completed_by=user_id,
            completed_at=datetime.now(timezone.utc),
            completion_comment=comment,
        )
        return task

    async def get_completed_tasks(self, project_id: str, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await self._check_project_member(project_id, user_id)
        return await self.task_repo.get_completed(project_id)

    async def delete_task(self, project_id: str, task_id: int, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await self._check_admin(project_id, user_id)

        task = await self.task_repo.get_by_id(task_id)
        if not task or task.project_id != project_id:
            raise HTTPException(status_code=404, detail="Task not found")

        await self.task_repo.delete(task)
