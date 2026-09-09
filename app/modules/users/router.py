from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.auth.security import require_roles
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    UserCreateRequest,
    UserResponse,
    UserRoleUpdateRequest,
)
from app.modules.users.service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(session: AsyncSession) -> UserService:
    return UserService(session, UserRepository(session))


@router.get("", response_model=list[UserResponse])
async def get_users(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
) -> list[UserResponse]:
    return await get_user_service(session).get_all()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("ADMIN"))],
) -> UserResponse:
    return await get_user_service(session).create(data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
) -> UserResponse:
    return await get_user_service(session).get_by_id(user_id)


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    data: UserRoleUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("ADMIN"))],
) -> UserResponse:
    return await get_user_service(session).update_role(user_id, data.role)


@router.delete("/{user_id}", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("ADMIN"))],
) -> UserResponse:
    return await get_user_service(session).deactivate(current_user, user_id)