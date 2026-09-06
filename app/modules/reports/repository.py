from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.tasks.model import ReportTask
from app.modules.versions.model import ReportVersion

from app.modules.reports.model import Report


class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, report_id: int) -> Report | None:
        result = await self.session.execute(select(Report).where(Report.id == report_id))
        return result.scalar_one_or_none()

    async def get_by_user_and_week(self, user_id: int, week_start: date) -> Report | None:
        result = await self.session.execute(select(Report).where(Report.user_id == user_id, Report.week_start == week_start))
        return result.scalar_one_or_none()

    async def get_page(
        self,
        page: int,
        page_size: int,
        user_id: int | None = None,
        report_status: str | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ) -> tuple[list[Report], int]:
        conditions = []

        if user_id is not None:
            conditions.append(Report.user_id == user_id)
        if report_status is not None:
            conditions.append(Report.status == report_status)
        if week_start_from is not None:
            conditions.append(Report.week_start >= week_start_from)
        if week_start_to is not None:
            conditions.append(Report.week_start <= week_start_to)

        if project_id is not None:
            latest_version_number = select(func.max(ReportVersion.version_number)).where(ReportVersion.report_id == Report.id).correlate(Report).scalar_subquery()

            project_exists = (
                select(ReportTask.id)
                .join(ReportVersion, ReportTask.report_version_id == ReportVersion.id)
                .where(
                    ReportVersion.report_id == Report.id,
                    ReportVersion.version_number == latest_version_number,
                    ReportTask.project_id == project_id,
                )
                .exists()
            )

            conditions.append(project_exists)

        total = (await self.session.execute(select(func.count()).select_from(Report).where(*conditions))).scalar_one()

        result = await self.session.execute(
            select(Report)
            .where(*conditions)
            .order_by(Report.week_start.desc(), Report.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        return list(result.scalars().all()), total

    def add(self, report: Report) -> None:
        self.session.add(report)