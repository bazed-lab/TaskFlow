from pydantic import BaseModel, Field, EmailStr, ConfigDict


#-------------Request-------------

#POST /auth/signup
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    username: str = Field(min_length=3, max_length=50)

#POST /auth/login
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

#POST /auth/refresh
#POST /auth/logout
class RefreshTokenRequest(BaseModel):
    refresh_token: str

#PATCH /users/me
class UserUpdateRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None

#-------------Response-------------

#POST /auth/signup
class MessageResponse(BaseModel):
    message: str

#POST /auth/login
#POST /auth/refresh
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

#GET /users/me
#POST /auth/signup
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_superuser: bool = False

    model_config = ConfigDict(from_attributes=True)