from datetime import datetime, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achievements.model import ReportAchievement
from app.modules.achievements.repository import ReportAchievementRepository
from app.modules.achievements.schemas import ReportAchievementResponse
from app.modules.blockers.model import ReportBlocker
from app.modules.blockers.repository import ReportBlockerRepository
from app.modules.blockers.schemas import ReportBlockerResponse
from app.modules.reports.model import Report
from app.modules.reports.repository import ReportRepository
from app.modules.reports.schemas import PaginatedReportsResponse, ReportCreateRequest, ReportListItemResponse, ReportResponse, ReportUpdateRequest
from app.modules.reviews.model import ReportReview
from app.modules.reviews.repository import ReportReviewRepository
from app.modules.reviews.schemas import ReviewResponse
from app.modules.tasks.model import ReportTask
from app.modules.tasks.repository import ReportTaskRepository
from app.modules.tasks.schemas import ReportTaskResponse
from app.modules.users.model import User
from app.modules.versions.model import ReportVersion
from app.modules.versions.repository import ReportVersionRepository
from app.modules.versions.schemas import ReportVersionHistoryResponse, ReportVersionResponse
from datetime import date, datetime, time, timedelta


class ReportService:
    def __init__(
        self,
        session: AsyncSession,
        report_repository: ReportRepository,
        version_repository: ReportVersionRepository,
        task_repository: ReportTaskRepository,
        blocker_repository: ReportBlockerRepository,
        achievement_repository: ReportAchievementRepository,
        review_repository: ReportReviewRepository,
    ):
        self.session = session
        self.report_repository = report_repository
        self.version_repository = version_repository
        self.task_repository = task_repository
        self.blocker_repository = blocker_repository
        self.achievement_repository = achievement_repository
        self.review_repository = review_repository

    async def create_draft(self, current_user: User, data: ReportCreateRequest) -> ReportResponse:
        if data.week_start.weekday() != 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="The reporting week must start on Monday.")

        existing_report = await self.report_repository.get_by_user_and_week(current_user.id, data.week_start)
        if existing_report is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A report already exists for this week.")

        if sum(1 for blocker in data.blockers if blocker.is_key_issue) > 1:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only one blocker can be marked as the key issue.")

        if sum(1 for achievement in data.achievements if achievement.is_key_achievement) > 1:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only one achievement can be marked as the key achievement.")

        week_end = data.week_start + timedelta(days=6)
        due_at = datetime.combine(week_end + timedelta(days=1), time(hour=9))

        report = Report(user_id=current_user.id, week_start=data.week_start, week_end=week_end, due_at=due_at, status="DRAFT")
        self.report_repository.add(report)
        await self.session.flush()

        version = ReportVersion(report_id=report.id, version_number=1, notes=data.notes)
        self.version_repository.add(version)
        await self.session.flush()

        tasks = [
            ReportTask(
                report_version_id=version.id,
                project_id=task.project_id,
                section=task.section,
                task_type=task.task_type,
                name=task.name.strip(),
                priority=task.priority,
                planned_percent=task.planned_percent,
                actual_percent=task.actual_percent,
                status=task.status,
                planned_hours=task.planned_hours,
                spent_hours=task.spent_hours,
                output=task.output,
            )
            for task in data.tasks
        ]

        blockers = [
            ReportBlocker(
                report_version_id=version.id,
                title=blocker.title.strip(),
                description=blocker.description,
                status=blocker.status,
                is_key_issue=blocker.is_key_issue,
            )
            for blocker in data.blockers
        ]

        achievements = [
            ReportAchievement(
                report_version_id=version.id,
                title=achievement.title.strip(),
                description=achievement.description,
                is_key_achievement=achievement.is_key_achievement,
            )
            for achievement in data.achievements
        ]

        if tasks:
            self.task_repository.add_all(tasks)
        if blockers:
            self.blocker_repository.add_all(blockers)
        if achievements:
            self.achievement_repository.add_all(achievements)

        await self.session.commit()
        await self.session.refresh(report)
        return await self.build_response(report)

    async def update_draft(self, current_user: User, report_id: int, data: ReportUpdateRequest) -> ReportResponse:
        report = await self.report_repository.get_by_id(report_id)
        if report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
        if report.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own report.")
        if report.status not in {"DRAFT", "NEEDS_CORRECTION"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only draft or correction-requested reports can be edited.")

        version = await self.version_repository.get_latest(report.id)
        if version is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Report version not found.")

        if "notes" in data.model_fields_set:
            version.notes = data.notes

        if data.tasks is not None:
            await self.task_repository.delete_by_version(version.id)

            tasks = [
                ReportTask(
                    report_version_id=version.id,
                    project_id=task.project_id,
                    section=task.section,
                    task_type=task.task_type,
                    name=task.name.strip(),
                    priority=task.priority,
                    planned_percent=task.planned_percent,
                    actual_percent=task.actual_percent,
                    status=task.status,
                    planned_hours=task.planned_hours,
                    spent_hours=task.spent_hours,
                    output=task.output,
                )
                for task in data.tasks
            ]

            if tasks:
                self.task_repository.add_all(tasks)

        if data.blockers is not None:
            if sum(1 for blocker in data.blockers if blocker.is_key_issue) > 1:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only one blocker can be marked as the key issue.")

            await self.blocker_repository.delete_by_version(version.id)

            blockers = [
                ReportBlocker(
                    report_version_id=version.id,
                    title=blocker.title.strip(),
                    description=blocker.description,
                    status=blocker.status,
                    is_key_issue=blocker.is_key_issue,
                )
                for blocker in data.blockers
            ]

            if blockers:
                self.blocker_repository.add_all(blockers)

        if data.achievements is not None:
            if sum(1 for achievement in data.achievements if achievement.is_key_achievement) > 1:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only one achievement can be marked as the key achievement.")

            await self.achievement_repository.delete_by_version(version.id)

            achievements = [
                ReportAchievement(
                    report_version_id=version.id,
                    title=achievement.title.strip(),
                    description=achievement.description,
                    is_key_achievement=achievement.is_key_achievement,
                )
                for achievement in data.achievements
            ]

            if achievements:
                self.achievement_repository.add_all(achievements)

        report.updated_at = datetime.now()
        await self.session.commit()
        await self.session.refresh(report)
        return await self.build_response(report)

    async def submit_report(self, current_user: User, report_id: int) -> ReportResponse:
        report = await self.report_repository.get_by_id(report_id)
        if report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
        if report.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only submit your own report.")
        if report.status not in {"DRAFT", "NEEDS_CORRECTION"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only draft or correction-requested reports can be submitted.")

        version = await self.version_repository.get_latest(report.id)
        if version is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Report version not found.")

        tasks = await self.task_repository.get_by_version(version.id)
        this_week_tasks = [task for task in tasks if task.section == "THIS_WEEK"]

        if not this_week_tasks:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one current-week task is required before submission.")

        for task in this_week_tasks:
            if task.priority is None or task.planned_percent is None or task.actual_percent is None or task.status is None or task.planned_hours is None or task.spent_hours is None:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Current-week tasks must include priority, planned percentage, actual percentage, status, planned hours, and spent hours.")

        submitted_at = datetime.now()
        version.submitted_at = submitted_at
        report.status = "SUBMITTED"
        report.updated_at = submitted_at

        await self.session.commit()
        await self.session.refresh(report)
        return await self.build_response(report)

    async def request_changes(self, current_user: User, report_id: int, comment: str) -> ReportResponse:
        report = await self.report_repository.get_by_id(report_id)
        if report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
        if report.status != "SUBMITTED":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only submitted reports can be sent back for correction.")

        current_version = await self.version_repository.get_latest(report.id)
        if current_version is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Report version not found.")

        current_tasks = await self.task_repository.get_by_version(current_version.id)
        current_blockers = await self.blocker_repository.get_by_version(current_version.id)
        current_achievements = await self.achievement_repository.get_by_version(current_version.id)

        review = ReportReview(report_version_id=current_version.id, reviewer_id=current_user.id, action="REQUEST_CHANGES", comment=comment.strip())
        self.review_repository.add(review)

        new_version = ReportVersion(report_id=report.id, version_number=current_version.version_number + 1, notes=current_version.notes)
        self.version_repository.add(new_version)
        await self.session.flush()

        new_tasks = [
            ReportTask(
                report_version_id=new_version.id,
                project_id=task.project_id,
                section=task.section,
                task_type=task.task_type,
                name=task.name,
                priority=task.priority,
                planned_percent=task.planned_percent,
                actual_percent=task.actual_percent,
                status=task.status,
                planned_hours=task.planned_hours,
                spent_hours=task.spent_hours,
                output=task.output,
            )
            for task in current_tasks
        ]

        new_blockers = [
            ReportBlocker(
                report_version_id=new_version.id,
                title=blocker.title,
                description=blocker.description,
                status=blocker.status,
                is_key_issue=blocker.is_key_issue,
            )
            for blocker in current_blockers
        ]

        new_achievements = [
            ReportAchievement(
                report_version_id=new_version.id,
                title=achievement.title,
                description=achievement.description,
                is_key_achievement=achievement.is_key_achievement,
            )
            for achievement in current_achievements
        ]

        if new_tasks:
            self.task_repository.add_all(new_tasks)
        if new_blockers:
            self.blocker_repository.add_all(new_blockers)
        if new_achievements:
            self.achievement_repository.add_all(new_achievements)

        report.status = "NEEDS_CORRECTION"
        report.updated_at = datetime.now()

        await self.session.commit()
        await self.session.refresh(report)
        return await self.build_response(report)

    async def approve_report(self, current_user: User, report_id: int) -> ReportResponse:
        report = await self.report_repository.get_by_id(report_id)
        if report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
        if report.status != "SUBMITTED":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only submitted reports can be approved.")

        version = await self.version_repository.get_latest(report.id)
        if version is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Report version not found.")

        review = ReportReview(report_version_id=version.id, reviewer_id=current_user.id, action="APPROVE", comment=None)
        self.review_repository.add(review)

        report.status = "APPROVED"
        report.updated_at = datetime.now()

        await self.session.commit()
        await self.session.refresh(report)
        return await self.build_response(report)

    async def get_reports(
        self,
        current_user: User,
        page: int,
        page_size: int,
        user_id: int | None = None,
        report_status: str | None = None,
        project_id: int | None = None,
        week_start_from: date | None = None,
        week_start_to: date | None = None,
    ) -> PaginatedReportsResponse:
        if week_start_from and week_start_to and week_start_from > week_start_to:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="week_start_from cannot be after week_start_to.")

        if current_user.role == "TEAM_MEMBER":
            user_id = current_user.id
        elif current_user.role not in {"MANAGER", "ADMIN"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view reports.")

        reports, total = await self.report_repository.get_page(
            page=page,
            page_size=page_size,
            user_id=user_id,
            report_status=report_status,
            project_id=project_id,
            week_start_from=week_start_from,
            week_start_to=week_start_to,
        )

        return PaginatedReportsResponse(
            page=page,
            page_size=page_size,
            total=total,
            items=[ReportListItemResponse.model_validate(report) for report in reports],
        )

    async def get_report_detail(self, current_user: User, report_id: int) -> ReportResponse:
        report = await self.report_repository.get_by_id(report_id)
        if report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

        if current_user.role == "TEAM_MEMBER" and report.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this report.")

        if current_user.role in {"MANAGER", "ADMIN"} and report.status == "DRAFT":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Draft report content is private to the report owner.")

        return await self.build_response(report)

    async def build_response(self, report: Report) -> ReportResponse:
        version = await self.version_repository.get_latest(report.id)
        if version is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Report version not found.")

        tasks = await self.task_repository.get_by_version(version.id)
        blockers = await self.blocker_repository.get_by_version(version.id)
        achievements = await self.achievement_repository.get_by_version(version.id)
        latest_review = await self.review_repository.get_latest_by_report(report.id)

        return ReportResponse(
            id=report.id,
            user_id=report.user_id,
            week_start=report.week_start,
            week_end=report.week_end,
            due_at=report.due_at,
            status=report.status,
            created_at=report.created_at,
            updated_at=report.updated_at,
            current_version=ReportVersionResponse(
                id=version.id,
                version_number=version.version_number,
                notes=version.notes,
                submitted_at=version.submitted_at,
                tasks=[ReportTaskResponse.model_validate(task) for task in tasks],
                blockers=[ReportBlockerResponse.model_validate(blocker) for blocker in blockers],
                achievements=[ReportAchievementResponse.model_validate(achievement) for achievement in achievements],
            ),
            latest_review=ReviewResponse.model_validate(latest_review) if latest_review else None,
        )

    async def get_version_history(self, current_user: User, report_id: int) -> list[ReportVersionHistoryResponse]:
        report = await self.report_repository.get_by_id(report_id)
        if report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

        if current_user.role == "TEAM_MEMBER" and report.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this report.")

        if current_user.role in {"MANAGER", "ADMIN"} and report.status == "DRAFT":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Draft report content is private to the report owner.")

        versions = await self.version_repository.get_all(report.id)
        return [await self.build_version_history_response(version) for version in versions]

    async def get_version_detail(self, current_user: User, report_id: int, version_number: int) -> ReportVersionHistoryResponse:
        report = await self.report_repository.get_by_id(report_id)
        if report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

        if current_user.role == "TEAM_MEMBER" and report.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this report.")

        if current_user.role in {"MANAGER", "ADMIN"} and report.status == "DRAFT":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Draft report content is private to the report owner.")

        versions = await self.version_repository.get_all(report.id)
        version = next((item for item in versions if item.version_number == version_number), None)

        if version is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report version not found.")

        return await self.build_version_history_response(version)

    async def build_version_history_response(self, version: ReportVersion) -> ReportVersionHistoryResponse:
        tasks = await self.task_repository.get_by_version(version.id)
        blockers = await self.blocker_repository.get_by_version(version.id)
        achievements = await self.achievement_repository.get_by_version(version.id)
        reviews = await self.review_repository.get_by_version(version.id)

        return ReportVersionHistoryResponse(
            id=version.id,
            version_number=version.version_number,
            notes=version.notes,
            submitted_at=version.submitted_at,
            tasks=[ReportTaskResponse.model_validate(task) for task in tasks],
            blockers=[ReportBlockerResponse.model_validate(blocker) for blocker in blockers],
            achievements=[ReportAchievementResponse.model_validate(achievement) for achievement in achievements],
            reviews=[ReviewResponse.model_validate(review) for review in reviews],
        )