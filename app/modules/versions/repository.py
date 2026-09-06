from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.versions.model import ReportVersion


class ReportVersionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        version_id: int,
    ) -> ReportVersion | None:
        return await self.session.get(
            ReportVersion,
            version_id,
        )

    async def get_latest(
        self,
        report_id: int,
    ) -> ReportVersion | None:
        result = await self.session.execute(
            select(ReportVersion)
            .where(
                ReportVersion.report_id == report_id,
            )
            .order_by(
                ReportVersion.version_number.desc(),
            )
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        report_id: int,
    ) -> list[ReportVersion]:
        result = await self.session.execute(
            select(ReportVersion)
            .where(
                ReportVersion.report_id == report_id,
            )
            .order_by(
                ReportVersion.version_number,
            )
        )

        return list(result.scalars().all())

    def add(
        self,
        version: ReportVersion,
    ) -> None:
        self.session.add(version)