from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProjectCreateRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
    )
    description: str | None = None


class ProjectUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    description: str | None = None


class ProjectMemberUpdateRequest(BaseModel):
    user_ids: list[int]


class ProjectMemberResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    members: list[ProjectMemberResponse] = Field(
        default_factory=list,
        validation_alias="users",
    )

    model_config = ConfigDict(
        from_attributes=True,
    )