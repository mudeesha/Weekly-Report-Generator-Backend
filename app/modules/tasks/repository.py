from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tasks.model import ReportTask


class ReportTaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_version(
        self,
        report_version_id: int,
    ) -> list[ReportTask]:
        result = await self.session.execute(
            select(ReportTask)
            .where(
                ReportTask.report_version_id
                == report_version_id
            )
            .order_by(ReportTask.id)
        )

        return list(result.scalars().all())

    def add_all(
        self,
        tasks: list[ReportTask],
    ) -> None:
        self.session.add_all(tasks)

    async def delete_by_version(
        self,
        report_version_id: int,
    ) -> None:
        await self.session.execute(
            delete(ReportTask).where(
                ReportTask.report_version_id
                == report_version_id
            )
        )