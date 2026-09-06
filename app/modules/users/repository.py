from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.model import User


class UserRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        result = await self.session.execute(
            select(User).where(
                User.email == email,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        return await self.session.get(
            User,
            user_id,
        )

    async def get_all(self) -> list[User]:
        result = await self.session.execute(
            select(User).order_by(User.name)
        )

        return list(
            result.scalars().all()
        )

    def add(
        self,
        user: User,
    ) -> None:
        self.session.add(user)