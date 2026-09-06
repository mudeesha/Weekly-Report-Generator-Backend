from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.auth.security import require_roles
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    UserResponse,
    UserRoleUpdateRequest,
)
from app.modules.users.service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=list[UserResponse],
)
async def get_users(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    current_user: Annotated[
        User,
        Depends(require_roles("ADMIN")),
    ],
) -> list[UserResponse]:
    user_repository = UserRepository(session)

    user_service = UserService(
        session,
        user_repository,
    )

    users = await user_service.get_all()

    return [
        UserResponse.model_validate(user)
        for user in users
    ]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: int,
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    current_user: Annotated[
        User,
        Depends(
            require_roles(
                "MANAGER",
                "ADMIN",
            )
        ),
    ],
) -> UserResponse:
    user_repository = UserRepository(session)

    user_service = UserService(
        session,
        user_repository,
    )

    user = await user_service.get_by_id(
        user_id,
    )

    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
)
async def update_user_role(
    user_id: int,
    data: UserRoleUpdateRequest,
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    current_user: Annotated[
        User,
        Depends(require_roles("ADMIN")),
    ],
) -> UserResponse:
    user_repository = UserRepository(session)

    user_service = UserService(
        session,
        user_repository,
    )

    user = await user_service.update_role(
        user_id,
        data.role,
    )

    return UserResponse.model_validate(user)