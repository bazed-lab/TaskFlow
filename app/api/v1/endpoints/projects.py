from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from schemas.auth import MessageResponse
from schemas.project import (
    CreateProjectRequest, ProjectResponse, ProjectDetailResponse,
    ProjectMemberResponse, AddProjectMemberRequest, UpdateMemberRoleRequest,
    JoinProjectRequest,
)
from services.project_service import ProjectService
from api.v1.endpoints.auth import get_current_user

project_router = APIRouter()


@project_router.post("", response_model=ProjectResponse, status_code=201, summary="Создать проект")
async def create_project(
    payload: CreateProjectRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Создаёт новый проект. Создатель автоматически становится admin."""
    service = ProjectService(session)
    project = await service.create_project(
        name=payload.name,
        description=payload.description,
        secret_key=payload.secret_key,
        owner_id=current_user.id,
    )
    return project


@project_router.get("", response_model=list[ProjectResponse], summary="Список проектов")
async def get_projects(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Возвращает все проекты, где текущий пользователь является участником."""
    service = ProjectService(session)
    return await service.get_user_projects(current_user.id)


@project_router.post("/join", response_model=ProjectMemberResponse, status_code=201, summary="Присоединиться по приглашению")
async def join_project(
    payload: JoinProjectRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Вступление в проект по ссылке вида UUID/SECRET_KEY."""
    service = ProjectService(session)
    return await service.join_project(payload.invite, current_user.id)


@project_router.get("/{project_id}", response_model=ProjectDetailResponse, summary="Детали проекта")
async def get_project(
    project_id: str,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Возвращает информацию о проекте и список его участников."""
    service = ProjectService(session)
    project, members = await service.get_project(project_id, current_user.id)
    return ProjectDetailResponse(project=project, members=members)


@project_router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=201, summary="Добавить участника")
async def add_member(
    project_id: str,
    payload: AddProjectMemberRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Добавляет пользователя в проект. Только для admin."""
    service = ProjectService(session)
    member = await service.add_member(
        project_id=project_id,
        current_user_id=current_user.id,
        handle=payload.handle,
        role=payload.role,
    )
    return member


@project_router.patch("/{project_id}/members/{user_id}", response_model=ProjectMemberResponse, summary="Изменить роль участника")
async def update_member_role(
    project_id: str,
    user_id: int,
    payload: UpdateMemberRoleRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Меняет роль участника (admin/member). Только для admin."""
    service = ProjectService(session)
    member = await service.update_member_role(
        project_id=project_id,
        current_user_id=current_user.id,
        target_user_id=user_id,
        role=payload.role,
    )
    return member


@project_router.delete("/{project_id}/members/{user_id}", response_model=MessageResponse, summary="Удалить участника")
async def remove_member(
    project_id: str,
    user_id: int,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Удаляет участника из проекта. Нельзя удалить владельца. Только для admin."""
    service = ProjectService(session)
    await service.remove_member(project_id, current_user.id, user_id)
    return MessageResponse(message="Member removed")
