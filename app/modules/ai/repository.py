from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achievements.model import ReportAchievement
from app.modules.blockers.model import ReportBlocker
from app.modules.projects.model import Project
from app.modules.reports.model import Report
from app.modules.tasks.model import ReportTask
from app.modules.users.model import User
from app.modules.versions.model import ReportVersion


class AIRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_report_context(self, week_start_from: date) -> list[dict]:
        latest_submitted_versions = (
            select(
                ReportVersion.report_id,
                func.max(ReportVersion.version_number).label("version_number"),
            )
            .where(ReportVersion.submitted_at.is_not(None))
            .group_by(ReportVersion.report_id)
            .subquery()
        )

        result = await self.session.execute(
            select(
                Report.id.label("report_id"),
                Report.user_id,
                User.name.label("user_name"),
                Report.week_start,
                Report.week_end,
                Report.status,
                ReportVersion.id.label("version_id"),
                ReportVersion.version_number,
                ReportVersion.notes,
                ReportVersion.submitted_at,
            )
            .select_from(Report)
            .join(User, Report.user_id == User.id)
            .join(latest_submitted_versions, latest_submitted_versions.c.report_id == Report.id)
            .join(
                ReportVersion,
                (ReportVersion.report_id == Report.id)
                & (ReportVersion.version_number == latest_submitted_versions.c.version_number),
            )
            .where(Report.week_start >= week_start_from)
            .order_by(Report.week_start.desc(), User.name)
        )

        reports = []

        for row in result.all():
            tasks_result = await self.session.execute(
                select(
                    ReportTask.section,
                    ReportTask.task_type,
                    ReportTask.name,
                    ReportTask.priority,
                    ReportTask.status,
                    ReportTask.planned_percent,
                    ReportTask.actual_percent,
                    ReportTask.planned_hours,
                    ReportTask.spent_hours,
                    ReportTask.output,
                    Project.id.label("project_id"),
                    Project.name.label("project_name"),
                )
                .join(Project, ReportTask.project_id == Project.id)
                .where(ReportTask.report_version_id == row.version_id)
            )

            blockers_result = await self.session.execute(
                select(
                    ReportBlocker.title,
                    ReportBlocker.description,
                    ReportBlocker.status,
                    ReportBlocker.is_key_issue,
                )
                .where(ReportBlocker.report_version_id == row.version_id)
            )

            achievements_result = await self.session.execute(
                select(
                    ReportAchievement.title,
                    ReportAchievement.description,
                    ReportAchievement.is_key_achievement,
                )
                .where(ReportAchievement.report_version_id == row.version_id)
            )

            tasks = [
                {
                    "section": task.section,
                    "type": task.task_type,
                    "name": task.name,
                    "project_id": task.project_id,
                    "project": task.project_name,
                    "priority": task.priority,
                    "status": task.status,
                    "planned_percent": task.planned_percent,
                    "actual_percent": task.actual_percent,
                    "planned_hours": float(task.planned_hours) if task.planned_hours is not None else None,
                    "spent_hours": float(task.spent_hours) if task.spent_hours is not None else None,
                    "output": task.output,
                }
                for task in tasks_result.all()
            ]

            blockers = [
                {
                    "title": blocker.title,
                    "description": blocker.description,
                    "status": blocker.status,
                    "is_key_issue": blocker.is_key_issue,
                }
                for blocker in blockers_result.all()
            ]

            achievements = [
                {
                    "title": achievement.title,
                    "description": achievement.description,
                    "is_key_achievement": achievement.is_key_achievement,
                }
                for achievement in achievements_result.all()
            ]

            reports.append(
                {
                    "report_id": row.report_id,
                    "member_id": row.user_id,
                    "member": row.user_name,
                    "week_start": row.week_start.isoformat(),
                    "week_end": row.week_end.isoformat(),
                    "report_status": row.status,
                    "version": row.version_number,
                    "submitted_at": row.submitted_at.isoformat(),
                    "notes": row.notes,
                    "tasks": tasks,
                    "blockers": blockers,
                    "achievements": achievements,
                }
            )

        return reports