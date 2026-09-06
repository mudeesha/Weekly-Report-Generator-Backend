from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.blockers.model import ReportBlocker


class ReportBlockerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_version(
        self,
        report_version_id: int,
    ) -> list[ReportBlocker]:
        result = await self.session.execute(
            select(ReportBlocker)
            .where(
                ReportBlocker.report_version_id
                == report_version_id
            )
            .order_by(ReportBlocker.id)
        )

        return list(result.scalars().all())

    def add_all(
        self,
        blockers: list[ReportBlocker],
    ) -> None:
        self.session.add_all(blockers)

    async def delete_by_version(
        self,
        report_version_id: int,
    ) -> None:
        await self.session.execute(
            delete(ReportBlocker).where(
                ReportBlocker.report_version_id
                == report_version_id
            )
        )