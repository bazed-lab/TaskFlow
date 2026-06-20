from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    assigned_to: int | None = None
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")


class UpdateTaskRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    assigned_to: int | None = None
    status: str | None = Field(default=None, pattern="^(todo|in_progress|done)$")
    priority: str | None = Field(default=None, pattern="^(low|medium|high)$")


class TaskResponse(BaseModel):
    id: int
    project_id: str
    title: str
    description: str | None = None
    assigned_to: int | None = None
    created_by: int
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
