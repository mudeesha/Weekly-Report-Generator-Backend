from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.security import (
    INVITATION_TOKEN_EXPIRE_HOURS,
    create_invitation_token,
    decode_invitation_token,
    hash_password,
)
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserInviteAcceptRequest, UserInviteRequest, UserInviteResponse, UserRegisterRequest


class UserService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.session = session
        self.repository = repository

    async def register(self, data: UserRegisterRequest) -> User:
        email = data.email.lower()

        if await self.repository.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")

        user = User(
            name=data.name.strip(),
            email=email,
            password_hash=hash_password(data.password),
            role="TEAM_MEMBER",
            is_active=True,
        )

        self.repository.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def create_invitation(self, data: UserInviteRequest) -> UserInviteResponse:
        email = data.email.lower()

        if await self.repository.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")

        token = create_invitation_token(data.name.strip(), email, data.role)

        return UserInviteResponse(
            invitation_token=token,
            expires_in_hours=INVITATION_TOKEN_EXPIRE_HOURS,
        )

    async def accept_invitation(self, data: UserInviteAcceptRequest) -> User:
        try:
            payload = decode_invitation_token(data.token)
            name = str(payload["name"]).strip()
            email = str(payload["email"]).lower()
            role = str(payload["role"])
        except (InvalidTokenError, KeyError, TypeError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired invitation token.")

        if role not in {"TEAM_MEMBER", "MANAGER", "ADMIN"}:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid invitation token.")

        if await self.repository.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(data.password),
            role=role,
            is_active=True,
        )

        self.repository.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_all(self) -> list[User]:
        return await self.repository.get_all()

    async def get_by_id(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        return user

    async def update_role(self, user_id: int, role: str) -> User:
        user = await self.get_by_id(user_id)
        user.role = role

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def deactivate(self, current_user: User, user_id: int) -> User:
        user = await self.get_by_id(user_id)

        if user.id == current_user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You cannot deactivate your own account.")

        user.is_active = False

        await self.session.commit()
        await self.session.refresh(user)
        return user