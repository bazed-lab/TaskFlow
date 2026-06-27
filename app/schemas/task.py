from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    assigned_to: int | None = None
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    deadline: datetime | None = None


class UpdateTaskRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    assigned_to: int | None = None
    status: str | None = Field(default=None, pattern="^(todo|in_progress|done)$")
    priority: str | None = Field(default=None, pattern="^(low|medium|high)$")
    deadline: datetime | None = None


class CompleteTaskRequest(BaseModel):
    comment: str | None = None


class TaskResponse(BaseModel):
    id: int
    project_id: str
    title: str
    description: str | None = None
    assigned_to: int | None = None
    created_by: int
    status: str
    priority: str
    deadline: datetime | None = None
    completed_by: int | None = None
    completed_at: datetime | None = None
    completion_comment: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CompletedTaskResponse(BaseModel):
    id: int
    project_id: str
    title: str
    description: str | None = None
    assigned_to: int | None = None
    created_by: int
    priority: str
    deadline: datetime | None = None
    completed_by: int
    completed_by_username: str
    completed_by_handle: str
    completed_at: datetime
    completion_comment: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
