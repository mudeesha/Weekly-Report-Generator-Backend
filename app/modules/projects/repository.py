from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.projects.model import Project


class ProjectRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_all(self) -> list[Project]:
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.users))
            .order_by(Project.name)
        )

        return list(
            result.scalars().all()
        )

    async def get_by_id(
        self,
        project_id: int,
    ) -> Project | None:
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.users))
            .where(Project.id == project_id)
        )

        return result.scalar_one_or_none()

    def add(
        self,
        project: Project,
    ) -> None:
        self.session.add(project)

    async def delete(
        self,
        project: Project,
    ) -> None:
        await self.session.delete(project)