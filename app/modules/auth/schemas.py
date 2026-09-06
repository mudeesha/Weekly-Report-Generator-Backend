from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr


UserRole = Literal["TEAM_MEMBER", "MANAGER", "ADMIN"]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)