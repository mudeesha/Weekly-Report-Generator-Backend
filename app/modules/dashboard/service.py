from datetime import date

from fastapi import HTTPException, status

from app.modules.dashboard.repository import DashboardRepository
from app.modules.dashboard.schemas import DashboardActivityResponse, DashboardSummaryResponse, ProjectHoursResponse, StatusDistributionResponse


class DashboardService:
    def __init__(self, repository: DashboardRepository):
        self.repository = repository

    def validate_date_range(self, week_start_from: date | None, week_start_to: date | None) -> None:
        if week_start_from and week_start_to and week_start_from > week_start_to:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="week_start_from cannot be after week_start_to.")

    async def get_summary(
        self,
        user_id: int | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ) -> DashboardSummaryResponse:
        self.validate_date_range(week_start_from, week_start_to)

        counts = await self.repository.get_report_counts(user_id, project_id, week_start_from, week_start_to)
        total_spent_hours = await self.repository.get_total_spent_hours(user_id, project_id, week_start_from, week_start_to)

        return DashboardSummaryResponse(
            total_reports=counts.total_reports,
            draft_reports=counts.draft_reports or 0,
            submitted_reports=counts.submitted_reports or 0,
            needs_correction_reports=counts.needs_correction_reports or 0,
            approved_reports=counts.approved_reports or 0,
            total_spent_hours=float(total_spent_hours),
        )

    async def get_status_distribution(
        self,
        user_id: int | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ) -> list[StatusDistributionResponse]:
        self.validate_date_range(week_start_from, week_start_to)
        rows = await self.repository.get_status_distribution(user_id, project_id, week_start_from, week_start_to)
        return [StatusDistributionResponse(status=row.status, count=row.count) for row in rows]

    async def get_hours_by_project(
        self,
        user_id: int | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ) -> list[ProjectHoursResponse]:
        self.validate_date_range(week_start_from, week_start_to)
        rows = await self.repository.get_hours_by_project(user_id, project_id, week_start_from, week_start_to)

        return [
            ProjectHoursResponse(
                project_id=row.project_id,
                project_name=row.project_name,
                spent_hours=float(row.spent_hours),
            )
            for row in rows
        ]

    async def get_activity_feed(
        self,
        limit: int,
        user_id: int | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ) -> list[DashboardActivityResponse]:
        self.validate_date_range(week_start_from, week_start_to)

        submissions = await self.repository.get_submission_activities(limit, user_id, project_id, week_start_from, week_start_to)
        reviews = await self.repository.get_review_activities(limit, user_id, project_id, week_start_from, week_start_to)
        activities: list[DashboardActivityResponse] = []

        for row in submissions:
            activities.append(
                DashboardActivityResponse(
                    activity_type="REPORT_SUBMITTED",
                    message=f"{row.user_name} submitted report Version {row.version_number}",
                    report_id=row.report_id,
                    version_number=row.version_number,
                    user_id=row.user_id,
                    user_name=row.user_name,
                    week_start=row.week_start,
                    created_at=row.created_at,
                )
            )

        for row in reviews:
            if row.action == "APPROVE":
                activity_type = "REPORT_APPROVED"
                message = f"{row.reviewer_name} approved {row.user_name}'s report"
            else:
                activity_type = "CHANGES_REQUESTED"
                message = f"{row.reviewer_name} requested changes to {row.user_name}'s report"

            activities.append(
                DashboardActivityResponse(
                    activity_type=activity_type,
                    message=message,
                    report_id=row.report_id,
                    version_number=row.version_number,
                    user_id=row.user_id,
                    user_name=row.user_name,
                    reviewer_id=row.reviewer_id,
                    reviewer_name=row.reviewer_name,
                    week_start=row.week_start,
                    created_at=row.created_at,
                )
            )

        activities.sort(key=lambda activity: activity.created_at, reverse=True)
        return activities[:limit]