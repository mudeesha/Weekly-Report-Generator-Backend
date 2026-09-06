from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achievements.model import ReportAchievement


class ReportAchievementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_version(
        self,
        report_version_id: int,
    ) -> list[ReportAchievement]:
        result = await self.session.execute(
            select(ReportAchievement)
            .where(
                ReportAchievement.report_version_id
                == report_version_id
            )
            .order_by(ReportAchievement.id)
        )

        return list(result.scalars().all())

    def add_all(
        self,
        achievements: list[ReportAchievement],
    ) -> None:
        self.session.add_all(achievements)

    async def delete_by_version(
        self,
        report_version_id: int,
    ) -> None:
        await self.session.execute(
            delete(ReportAchievement).where(
                ReportAchievement.report_version_id
                == report_version_id
            )
        )