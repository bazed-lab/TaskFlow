from fastapi import APIRouter

from api.v1.endpoints.auth import auth_router, users_router
from api.v1.endpoints.projects import project_router
from api.v1.endpoints.tasks import task_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(project_router, prefix="/projects", tags=["projects"])
api_router.include_router(task_router, prefix="/projects/{project_id}/tasks", tags=["tasks"])