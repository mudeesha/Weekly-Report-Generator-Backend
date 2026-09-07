from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.modules.dashboard.service import DashboardService


@pytest.mark.asyncio
async def test_dashboard_summary_maps_repository_values() -> None:
    counts = SimpleNamespace(
        total_reports=5,
        draft_reports=1,
        submitted_reports=1,
        needs_correction_reports=1,
        approved_reports=2,
    )

    repository = SimpleNamespace(
        get_report_counts=AsyncMock(return_value=counts),
        get_total_spent_hours=AsyncMock(return_value=24.5),
    )

    service = DashboardService(repository)

    result = await service.get_summary(
        user_id=2,
        project_id=1,
        week_start_from=date(2026, 9, 1),
        week_start_to=date(2026, 9, 30),
    )

    assert result.total_reports == 5
    assert result.approved_reports == 2
    assert result.total_spent_hours == 24.5

    repository.get_report_counts.assert_awaited_once_with(
        2,
        1,
        date(2026, 9, 1),
        date(2026, 9, 30),
    )


@pytest.mark.asyncio
async def test_dashboard_rejects_invalid_date_range() -> None:
    service = DashboardService(SimpleNamespace())

    with pytest.raises(HTTPException) as exc:
        await service.get_summary(
            week_start_from=date(2026, 10, 1),
            week_start_to=date(2026, 9, 1),
        )

    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_activity_feed_is_sorted_newest_first() -> None:
    submissions = [
        SimpleNamespace(
            report_id=1,
            version_number=1,
            user_id=2,
            user_name="John Doe",
            week_start=date(2026, 9, 7),
            created_at=datetime(2026, 9, 6, 18, 57),
        )
    ]

    reviews = [
        SimpleNamespace(
            report_id=1,
            version_number=1,
            action="APPROVE",
            user_id=2,
            user_name="John Doe",
            reviewer_id=1,
            reviewer_name="Admin User",
            week_start=date(2026, 9, 7),
            created_at=datetime(2026, 9, 6, 19, 10),
        )
    ]

    repository = SimpleNamespace(
        get_submission_activities=AsyncMock(return_value=submissions),
        get_review_activities=AsyncMock(return_value=reviews),
    )

    service = DashboardService(repository)

    result = await service.get_activity_feed(limit=10)

    assert len(result) == 2
    assert result[0].activity_type == "REPORT_APPROVED"
    assert result[1].activity_type == "REPORT_SUBMITTED"