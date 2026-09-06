from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.auth.security import require_roles
from app.modules.dashboard.repository import DashboardRepository
from app.modules.dashboard.schemas import DashboardActivityResponse, DashboardSummaryResponse, ProjectHoursResponse, StatusDistributionResponse
from app.modules.dashboard.service import DashboardService
from app.modules.users.model import User


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_dashboard_service(session: AsyncSession) -> DashboardService:
    return DashboardService(DashboardRepository(session))


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
    user_id: Annotated[int | None, Query(ge=1)] = None,
    project_id: Annotated[int | None, Query(ge=1)] = None,
    week_start_from: date | None = None,
    week_start_to: date | None = None,
) -> DashboardSummaryResponse:
    return await get_dashboard_service(session).get_summary(user_id, project_id, week_start_from, week_start_to)


@router.get("/status-distribution", response_model=list[StatusDistributionResponse])
async def get_status_distribution(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
    user_id: Annotated[int | None, Query(ge=1)] = None,
    project_id: Annotated[int | None, Query(ge=1)] = None,
    week_start_from: date | None = None,
    week_start_to: date | None = None,
) -> list[StatusDistributionResponse]:
    return await get_dashboard_service(session).get_status_distribution(user_id, project_id, week_start_from, week_start_to)


@router.get("/hours-by-project", response_model=list[ProjectHoursResponse])
async def get_hours_by_project(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
    user_id: Annotated[int | None, Query(ge=1)] = None,
    project_id: Annotated[int | None, Query(ge=1)] = None,
    week_start_from: date | None = None,
    week_start_to: date | None = None,
) -> list[ProjectHoursResponse]:
    return await get_dashboard_service(session).get_hours_by_project(user_id, project_id, week_start_from, week_start_to)


@router.get("/activity", response_model=list[DashboardActivityResponse])
async def get_activity_feed(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    user_id: Annotated[int | None, Query(ge=1)] = None,
    project_id: Annotated[int | None, Query(ge=1)] = None,
    week_start_from: date | None = None,
    week_start_to: date | None = None,
) -> list[DashboardActivityResponse]:
    return await get_dashboard_service(session).get_activity_feed(limit, user_id, project_id, week_start_from, week_start_to)