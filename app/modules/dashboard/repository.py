from datetime import date

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.modules.projects.model import Project
from app.modules.reports.model import Report
from app.modules.reviews.model import ReportReview
from app.modules.tasks.model import ReportTask
from app.modules.users.model import User
from app.modules.versions.model import ReportVersion


class DashboardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _latest_versions(self):
        return (
            select(
                ReportVersion.report_id,
                func.max(ReportVersion.version_number).label("version_number"),
            )
            .group_by(ReportVersion.report_id)
            .subquery()
        )

    def _report_conditions(
        self,
        user_id: int | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ):
        conditions = []

        if user_id is not None:
            conditions.append(Report.user_id == user_id)
        if week_start_from is not None:
            conditions.append(Report.week_start >= week_start_from)
        if week_start_to is not None:
            conditions.append(Report.week_start <= week_start_to)

        if project_id is not None:
            latest_version_number = (
                select(func.max(ReportVersion.version_number))
                .where(ReportVersion.report_id == Report.id)
                .correlate(Report)
                .scalar_subquery()
            )

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

        return conditions

    async def get_report_counts(
        self,
        user_id: int | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ):
        conditions = self._report_conditions(user_id, project_id, week_start_from, week_start_to)

        result = await self.session.execute(
            select(
                func.count(Report.id).label("total_reports"),
                func.sum(case((Report.status == "DRAFT", 1), else_=0)).label("draft_reports"),
                func.sum(case((Report.status == "SUBMITTED", 1), else_=0)).label("submitted_reports"),
                func.sum(case((Report.status == "NEEDS_CORRECTION", 1), else_=0)).label("needs_correction_reports"),
                func.sum(case((Report.status == "APPROVED", 1), else_=0)).label("approved_reports"),
            )
            .where(*conditions)
        )
        return result.one()

    async def get_total_spent_hours(
        self,
        user_id: int | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ):
        latest_versions = self._latest_versions()
        conditions = [ReportTask.section == "THIS_WEEK"]

        if user_id is not None:
            conditions.append(Report.user_id == user_id)
        if project_id is not None:
            conditions.append(ReportTask.project_id == project_id)
        if week_start_from is not None:
            conditions.append(Report.week_start >= week_start_from)
        if week_start_to is not None:
            conditions.append(Report.week_start <= week_start_to)

        result = await self.session.execute(
            select(func.coalesce(func.sum(ReportTask.spent_hours), 0))
            .select_from(ReportTask)
            .join(ReportVersion, ReportTask.report_version_id == ReportVersion.id)
            .join(
                latest_versions,
                and_(
                    ReportVersion.report_id == latest_versions.c.report_id,
                    ReportVersion.version_number == latest_versions.c.version_number,
                ),
            )
            .join(Report, ReportVersion.report_id == Report.id)
            .where(*conditions)
        )
        return result.scalar_one()

    async def get_status_distribution(
        self,
        user_id: int | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ):
        conditions = self._report_conditions(user_id, project_id, week_start_from, week_start_to)

        result = await self.session.execute(
            select(Report.status, func.count(Report.id).label("count"))
            .where(*conditions)
            .group_by(Report.status)
            .order_by(Report.status)
        )
        return result.all()

    async def get_hours_by_project(
        self,
        user_id: int | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ):
        latest_versions = self._latest_versions()
        conditions = [ReportTask.section == "THIS_WEEK"]

        if user_id is not None:
            conditions.append(Report.user_id == user_id)
        if project_id is not None:
            conditions.append(ReportTask.project_id == project_id)
        if week_start_from is not None:
            conditions.append(Report.week_start >= week_start_from)
        if week_start_to is not None:
            conditions.append(Report.week_start <= week_start_to)

        result = await self.session.execute(
            select(
                Project.id.label("project_id"),
                Project.name.label("project_name"),
                func.coalesce(func.sum(ReportTask.spent_hours), 0).label("spent_hours"),
            )
            .select_from(ReportTask)
            .join(ReportVersion, ReportTask.report_version_id == ReportVersion.id)
            .join(
                latest_versions,
                and_(
                    ReportVersion.report_id == latest_versions.c.report_id,
                    ReportVersion.version_number == latest_versions.c.version_number,
                ),
            )
            .join(Report, ReportVersion.report_id == Report.id)
            .join(Project, ReportTask.project_id == Project.id)
            .where(*conditions)
            .group_by(Project.id, Project.name)
            .order_by(func.sum(ReportTask.spent_hours).desc())
        )
        return result.all()

    async def get_submission_activities(
        self,
        limit: int,
        user_id: int | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ):
        conditions = [ReportVersion.submitted_at.is_not(None)]

        if user_id is not None:
            conditions.append(Report.user_id == user_id)
        if week_start_from is not None:
            conditions.append(Report.week_start >= week_start_from)
        if week_start_to is not None:
            conditions.append(Report.week_start <= week_start_to)

        if project_id is not None:
            project_exists = (
                select(ReportTask.id)
                .where(
                    ReportTask.report_version_id == ReportVersion.id,
                    ReportTask.project_id == project_id,
                )
                .correlate(ReportVersion)
                .exists()
            )
            conditions.append(project_exists)

        result = await self.session.execute(
            select(
                Report.id.label("report_id"),
                ReportVersion.version_number,
                ReportVersion.submitted_at.label("created_at"),
                Report.user_id,
                User.name.label("user_name"),
                Report.week_start,
            )
            .select_from(ReportVersion)
            .join(Report, ReportVersion.report_id == Report.id)
            .join(User, Report.user_id == User.id)
            .where(*conditions)
            .order_by(ReportVersion.submitted_at.desc())
            .limit(limit)
        )
        return result.all()

    async def get_review_activities(
        self,
        limit: int,
        user_id: int | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ):
        report_user = aliased(User)
        reviewer = aliased(User)
        conditions = []

        if user_id is not None:
            conditions.append(Report.user_id == user_id)
        if week_start_from is not None:
            conditions.append(Report.week_start >= week_start_from)
        if week_start_to is not None:
            conditions.append(Report.week_start <= week_start_to)

        if project_id is not None:
            project_exists = (
                select(ReportTask.id)
                .where(
                    ReportTask.report_version_id == ReportVersion.id,
                    ReportTask.project_id == project_id,
                )
                .correlate(ReportVersion)
                .exists()
            )
            conditions.append(project_exists)

        result = await self.session.execute(
            select(
                Report.id.label("report_id"),
                ReportVersion.version_number,
                ReportReview.action,
                ReportReview.created_at,
                Report.user_id,
                report_user.name.label("user_name"),
                ReportReview.reviewer_id,
                reviewer.name.label("reviewer_name"),
                Report.week_start,
            )
            .select_from(ReportReview)
            .join(ReportVersion, ReportReview.report_version_id == ReportVersion.id)
            .join(Report, ReportVersion.report_id == Report.id)
            .join(report_user, Report.user_id == report_user.id)
            .join(reviewer, ReportReview.reviewer_id == reviewer.id)
            .where(*conditions)
            .order_by(ReportReview.created_at.desc())
            .limit(limit)
        )
        return result.all()