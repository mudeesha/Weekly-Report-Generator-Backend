from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.achievements.repository import ReportAchievementRepository
from app.modules.auth.security import get_current_user, require_roles
from app.modules.blockers.repository import ReportBlockerRepository
from app.modules.projects.repository import ProjectRepository
from app.modules.reports.repository import ReportRepository
from app.modules.reports.schemas import PaginatedReportsResponse, ReportCreateRequest, ReportResponse, ReportStatus, ReportUpdateRequest
from app.modules.reports.service import ReportService
from app.modules.reviews.repository import ReportReviewRepository
from app.modules.reviews.schemas import RequestChangesRequest
from app.modules.tasks.repository import ReportTaskRepository
from app.modules.users.model import User
from app.modules.versions.repository import ReportVersionRepository
from app.modules.versions.schemas import ReportVersionHistoryResponse


router = APIRouter(prefix="/reports", tags=["Reports"])


def get_report_service(session: AsyncSession) -> ReportService:
    return ReportService(
        session=session,
        report_repository=ReportRepository(session),
        version_repository=ReportVersionRepository(session),
        task_repository=ReportTaskRepository(session),
        blocker_repository=ReportBlockerRepository(session),
        achievement_repository=ReportAchievementRepository(session),
        review_repository=ReportReviewRepository(session),
        project_repository=ProjectRepository(session),
    )


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    data: ReportCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("TEAM_MEMBER"))],
) -> ReportResponse:
    return await get_report_service(session).create_draft(current_user, data)


@router.get("", response_model=PaginatedReportsResponse)
async def get_reports(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    user_id: int | None = None,
    project_id: int | None = None,
    report_status: Annotated[ReportStatus | None, Query(alias="status")] = None,
    week_start_from: date | None = None,
    week_start_to: date | None = None,
) -> PaginatedReportsResponse:
    return await get_report_service(session).get_reports(
        current_user=current_user,
        page=page,
        page_size=page_size,
        user_id=user_id,
        project_id=project_id,
        report_status=report_status,
        week_start_from=week_start_from,
        week_start_to=week_start_to,
    )


@router.get("/{report_id}/versions", response_model=list[ReportVersionHistoryResponse])
async def get_report_versions(
    report_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[ReportVersionHistoryResponse]:
    return await get_report_service(session).get_version_history(current_user, report_id)


@router.get("/{report_id}/versions/{version_number}", response_model=ReportVersionHistoryResponse)
async def get_report_version(
    report_id: int,
    version_number: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ReportVersionHistoryResponse:
    return await get_report_service(session).get_version_detail(current_user, report_id, version_number)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ReportResponse:
    return await get_report_service(session).get_report_detail(current_user, report_id)


@router.patch("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    data: ReportUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("TEAM_MEMBER"))],
) -> ReportResponse:
    return await get_report_service(session).update_draft(current_user, report_id, data)


@router.post("/{report_id}/submit", response_model=ReportResponse)
async def submit_report(
    report_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("TEAM_MEMBER"))],
) -> ReportResponse:
    return await get_report_service(session).submit_report(current_user, report_id)


@router.post("/{report_id}/request-changes", response_model=ReportResponse)
async def request_changes(
    report_id: int,
    data: RequestChangesRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
) -> ReportResponse:
    return await get_report_service(session).request_changes(current_user, report_id, data.comment)


@router.post("/{report_id}/approve", response_model=ReportResponse)
async def approve_report(
    report_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
) -> ReportResponse:
    return await get_report_service(session).approve_report(current_user, report_id)