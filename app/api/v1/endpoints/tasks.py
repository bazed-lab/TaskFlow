from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from schemas.task import CreateTaskRequest, UpdateTaskRequest, TaskResponse
from schemas.auth import MessageResponse
from services.task_service import TaskService
from api.v1.endpoints.auth import get_current_user

task_router = APIRouter()


@task_router.post("", response_model=TaskResponse, status_code=201, summary="Создать задачу")
async def create_task(
    project_id: str,
    payload: CreateTaskRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Создаёт задачу в проекте. Только для admin."""
    service = TaskService(session)
    task = await service.create_task(
        project_id=project_id,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        assigned_to=payload.assigned_to,
        priority=payload.priority,
    )
    return task


@task_router.get("", response_model=list[TaskResponse], summary="Список задач")
async def get_tasks(
    project_id: str,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Возвращает все задачи проекта."""
    service = TaskService(session)
    return await service.get_tasks(project_id, current_user.id)


@task_router.get("/{task_id}", response_model=TaskResponse, summary="Детали задачи")
async def get_task(
    project_id: str,
    task_id: int,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Возвращает информацию о задаче."""
    service = TaskService(session)
    return await service.get_task(project_id, task_id, current_user.id)


@task_router.patch("/{task_id}", response_model=TaskResponse, summary="Обновить задачу")
async def update_task(
    project_id: str,
    task_id: int,
    payload: UpdateTaskRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Обновляет задачу. Admin может менять всё, исполнитель — только status."""
    service = TaskService(session)
    kwargs = {k: v for k, v in payload.model_dump().items() if v is not None}
    return await service.update_task(project_id, task_id, current_user.id, **kwargs)


@task_router.delete("/{task_id}", response_model=MessageResponse, summary="Удалить задачу")
async def delete_task(
    project_id: str,
    task_id: int,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Удаляет задачу. Только для admin."""
    service = TaskService(session)
    await service.delete_task(project_id, task_id, current_user.id)
    return MessageResponse(message="Task deleted")
