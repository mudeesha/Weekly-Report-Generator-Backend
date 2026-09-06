from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


UserRole = Literal["TEAM_MEMBER", "MANAGER", "ADMIN"]


class UserRegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRoleUpdateRequest(BaseModel):
    role: UserRole


class UserInviteRequest(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    role: UserRole = "TEAM_MEMBER"


class UserInviteResponse(BaseModel):
    invitation_token: str
    expires_in_hours: int


class UserInviteAcceptRequest(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)