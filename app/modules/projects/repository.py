from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.projects.model import Project
from app.modules.tasks.model import ReportTask


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Project]:
        result = await self.session.execute(select(Project).options(selectinload(Project.users)).order_by(Project.name))
        return list(result.scalars().all())

    async def get_by_id(self, project_id: int) -> Project | None:
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.users))
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def is_used_in_reports(self, project_id: int) -> bool:
        result = await self.session.execute(select(exists().where(ReportTask.project_id == project_id)))
        return bool(result.scalar())

    def add(self, project: Project) -> None:
        self.session.add(project)

    async def delete(self, project: Project) -> None:
        await self.session.delete(project)