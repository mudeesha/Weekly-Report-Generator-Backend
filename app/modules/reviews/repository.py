from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reviews.model import ReportReview
from app.modules.versions.model import ReportVersion


class ReportReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, review: ReportReview) -> None:
        self.session.add(review)

    async def get_by_version(self, version_id: int) -> list[ReportReview]:
        result = await self.session.execute(select(ReportReview).where(ReportReview.report_version_id == version_id).order_by(ReportReview.created_at, ReportReview.id))
        return list(result.scalars().all())

    async def get_latest_by_report(self, report_id: int) -> ReportReview | None:
        result = await self.session.execute(
            select(ReportReview)
            .join(ReportVersion, ReportReview.report_version_id == ReportVersion.id)
            .where(ReportVersion.report_id == report_id)
            .order_by(ReportReview.created_at.desc(), ReportReview.id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()