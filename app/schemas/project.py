from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


#-------------Request-------------

class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    secret_key: str | None = None


class AddProjectMemberRequest(BaseModel):
    user_id: int
    role: str = Field(default="member", pattern="^(admin|member)$")


class UpdateMemberRoleRequest(BaseModel):
    role: str = Field(pattern="^(admin|member)$")


class JoinProjectRequest(BaseModel):
    invite: str


#-------------Response-------------

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    secret_key: str | None = None
    owner_id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberResponse(BaseModel):
    id: int
    user_id: int
    role: str
    username: str

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(BaseModel):
    project: ProjectResponse
    members: list[ProjectMemberResponse]
