from app.modules.auth.security import (
    create_access_token,
    verify_password,
)
from app.modules.users.model import User
from app.modules.users.repository import UserRepository


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self.user_repository = user_repository

    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> User | None:
        user = await self.user_repository.get_by_email(email)

        if user is None:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user

    def create_token(
        self,
        user: User,
    ) -> str:
        return create_access_token(user.id)