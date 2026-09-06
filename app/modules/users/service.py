from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.security import hash_password
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    UserRegisterRequest,
    UserRole,
)


class UserService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ):
        self.session = session
        self.user_repository = user_repository

    async def register(
        self,
        data: UserRegisterRequest,
    ) -> User:
        email = str(data.email).lower()

        existing_user = await self.user_repository.get_by_email(
            email,
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        user = User(
            name=data.name.strip(),
            email=email,
            password_hash=hash_password(data.password),
            role="TEAM_MEMBER",
        )

        self.user_repository.add(user)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get_all(self) -> list[User]:
        return await self.user_repository.get_all()

    async def get_by_id(
        self,
        user_id: int,
    ) -> User:
        user = await self.user_repository.get_by_id(
            user_id,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        return user

    async def update_role(
        self,
        user_id: int,
        role: UserRole,
    ) -> User:
        user = await self.get_by_id(user_id)

        user.role = role

        await self.session.commit()
        await self.session.refresh(user)

        return user