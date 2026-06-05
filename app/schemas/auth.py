from pydantic import BaseModel, Field, EmailStr


class Auth(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class AuthLoginResponse(Auth):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

class AuthSingupResponse(BaseModel):
    email: EmailStr
    username: str

class AuthSingup(Auth):
    username: str

class AuthRefreshResponse(Auth):
    refresh_token: str
