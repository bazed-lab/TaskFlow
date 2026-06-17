from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from schemas.auth import MessageResponse
from schemas.project import (
    CreateProjectRequest, ProjectResponse, ProjectDetailResponse,
    ProjectMemberResponse, AddProjectMemberRequest, UpdateMemberRoleRequest,
)
from services.project_service import ProjectService
from api.v1.endpoints.auth import get_current_user

project_router = APIRouter()


@project_router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    payload: CreateProjectRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = ProjectService(session)
    project = await service.create_project(
        name=payload.name,
        description=payload.description,
        owner_id=current_user.id,
    )
    return project


@project_router.get("", response_model=list[ProjectResponse])
async def get_projects(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = ProjectService(session)
    return await service.get_user_projects(current_user.id)


@project_router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: str,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = ProjectService(session)
    project, members = await service.get_project(project_id, current_user.id)
    return ProjectDetailResponse(project=project, members=members)


@project_router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=201)
async def add_member(
    project_id: str,
    payload: AddProjectMemberRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = ProjectService(session)
    member = await service.add_member(
        project_id=project_id,
        current_user_id=current_user.id,
        target_user_id=payload.user_id,
        role=payload.role,
    )
    return member


@project_router.patch("/{project_id}/members/{user_id}", response_model=ProjectMemberResponse)
async def update_member_role(
    project_id: str,
    user_id: int,
    payload: UpdateMemberRoleRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = ProjectService(session)
    member = await service.update_member_role(
        project_id=project_id,
        current_user_id=current_user.id,
        target_user_id=user_id,
        role=payload.role,
    )
    return member


@project_router.delete("/{project_id}/members/{user_id}", response_model=MessageResponse)
async def remove_member(
    project_id: str,
    user_id: int,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = ProjectService(session)
    await service.remove_member(project_id, current_user.id, user_id)
    return MessageResponse(message="Member removed")
