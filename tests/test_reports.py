from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException

from app.modules.reports.service import ReportService
from app.modules.tasks.schemas import ReportTaskRequest


def make_report_service(fake_session):
    repositories = {
        "report": SimpleNamespace(),
        "version": SimpleNamespace(),
        "task": SimpleNamespace(),
        "blocker": SimpleNamespace(),
        "achievement": SimpleNamespace(),
        "review": SimpleNamespace(),
        "project": SimpleNamespace(),
    }

    service = ReportService(
        session=fake_session,
        report_repository=repositories["report"],
        version_repository=repositories["version"],
        task_repository=repositories["task"],
        blocker_repository=repositories["blocker"],
        achievement_repository=repositories["achievement"],
        review_repository=repositories["review"],
        project_repository=repositories["project"],
    )

    return service, repositories


@pytest.mark.asyncio
async def test_team_member_report_list_is_always_scoped_to_self(fake_session) -> None:
    service, repositories = make_report_service(fake_session)

    repositories["report"].get_page = AsyncMock(return_value=([], 0))
    current_user = SimpleNamespace(id=2, role="TEAM_MEMBER")

    await service.get_reports(
        current_user=current_user,
        page=1,
        page_size=10,
        user_id=999,
    )

    repositories["report"].get_page.assert_awaited_once_with(
        page=1,
        page_size=10,
        user_id=2,
        report_status=None,
        project_id=None,
        week_start_from=None,
        week_start_to=None,
    )


@pytest.mark.asyncio
async def test_report_rejects_nonexistent_project(fake_session) -> None:
    service, repositories = make_report_service(fake_session)

    repositories["project"].get_by_id = AsyncMock(return_value=None)
    current_user = SimpleNamespace(id=2)

    tasks = [
        ReportTaskRequest(
            project_id=9999,
            section="THIS_WEEK",
            task_type="TESTING",
            name="Invalid project task",
        )
    ]

    with pytest.raises(HTTPException) as exc:
        await service.validate_task_projects(current_user, tasks)

    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_report_rejects_unassigned_project(fake_session) -> None:
    service, repositories = make_report_service(fake_session)

    project = SimpleNamespace(
        id=5,
        users=[SimpleNamespace(id=10)],
    )

    repositories["project"].get_by_id = AsyncMock(return_value=project)
    current_user = SimpleNamespace(id=2)

    tasks = [
        ReportTaskRequest(
            project_id=5,
            section="THIS_WEEK",
            task_type="TESTING",
            name="Unassigned project task",
        )
    ]

    with pytest.raises(HTTPException) as exc:
        await service.validate_task_projects(current_user, tasks)

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_report_accepts_assigned_project(fake_session) -> None:
    service, repositories = make_report_service(fake_session)

    project = SimpleNamespace(
        id=1,
        users=[SimpleNamespace(id=2)],
    )

    repositories["project"].get_by_id = AsyncMock(return_value=project)
    current_user = SimpleNamespace(id=2)

    tasks = [
        ReportTaskRequest(
            project_id=1,
            section="THIS_WEEK",
            task_type="TESTING",
            name="Assigned project task",
        )
    ]

    await service.validate_task_projects(current_user, tasks)


@pytest.mark.asyncio
async def test_manager_sees_last_submitted_version_during_correction(fake_session) -> None:
    service, repositories = make_report_service(fake_session)

    report = SimpleNamespace(id=1, status="NEEDS_CORRECTION")

    version_1 = SimpleNamespace(
        id=1,
        version_number=1,
        submitted_at=datetime(2026, 9, 6, 18, 57),
    )

    version_2 = SimpleNamespace(
        id=2,
        version_number=2,
        submitted_at=None,
    )

    repositories["version"].get_latest = AsyncMock(return_value=version_2)
    repositories["version"].get_all = AsyncMock(return_value=[version_1, version_2])

    manager = SimpleNamespace(id=4, role="MANAGER")

    visible_version = await service.get_visible_version(report, manager)

    assert visible_version.version_number == 1


@pytest.mark.asyncio
async def test_member_sees_editable_version_during_correction(fake_session) -> None:
    service, repositories = make_report_service(fake_session)

    report = SimpleNamespace(id=1, status="NEEDS_CORRECTION")
    version_2 = SimpleNamespace(id=2, version_number=2, submitted_at=None)

    repositories["version"].get_latest = AsyncMock(return_value=version_2)

    member = SimpleNamespace(id=2, role="TEAM_MEMBER")

    visible_version = await service.get_visible_version(report, member)

    assert visible_version.version_number == 2


@pytest.mark.asyncio
async def test_submit_changes_report_status_to_submitted(fake_session) -> None:
    service, repositories = make_report_service(fake_session)

    report = SimpleNamespace(
        id=2,
        user_id=2,
        status="DRAFT",
        updated_at=None,
    )

    version = SimpleNamespace(
        id=3,
        version_number=1,
        submitted_at=None,
    )

    task = SimpleNamespace(
        section="THIS_WEEK",
        priority="HIGH",
        planned_percent=100,
        actual_percent=50,
        status="IN_PROGRESS",
        planned_hours=8,
        spent_hours=4,
    )

    repositories["report"].get_by_id = AsyncMock(return_value=report)
    repositories["version"].get_latest = AsyncMock(return_value=version)
    repositories["task"].get_by_version = AsyncMock(return_value=[task])

    service.build_response = AsyncMock(return_value=SimpleNamespace())
    current_user = SimpleNamespace(id=2, role="TEAM_MEMBER")

    await service.submit_report(current_user, 2)

    assert report.status == "SUBMITTED"
    assert version.submitted_at is not None
    fake_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_request_changes_creates_new_editable_version(fake_session) -> None:
    service, repositories = make_report_service(fake_session)

    report = SimpleNamespace(
        id=1,
        status="SUBMITTED",
        updated_at=None,
    )

    current_version = SimpleNamespace(
        id=1,
        version_number=1,
        notes="Original notes",
    )

    repositories["report"].get_by_id = AsyncMock(return_value=report)
    repositories["version"].get_latest = AsyncMock(return_value=current_version)
    repositories["version"].add = Mock()
    repositories["task"].get_by_version = AsyncMock(return_value=[])
    repositories["task"].add_all = Mock()
    repositories["blocker"].get_by_version = AsyncMock(return_value=[])
    repositories["blocker"].add_all = Mock()
    repositories["achievement"].get_by_version = AsyncMock(return_value=[])
    repositories["achievement"].add_all = Mock()
    repositories["review"].add = Mock()

    service.build_response = AsyncMock(return_value=SimpleNamespace())

    manager = SimpleNamespace(id=4, role="MANAGER")

    await service.request_changes(
        current_user=manager,
        report_id=1,
        comment="Please correct the report.",
    )

    assert report.status == "NEEDS_CORRECTION"

    review = repositories["review"].add.call_args.args[0]
    assert review.report_version_id == 1
    assert review.reviewer_id == 4
    assert review.action == "REQUEST_CHANGES"

    new_version = repositories["version"].add.call_args.args[0]
    assert new_version.version_number == 2
    assert new_version.submitted_at is None


@pytest.mark.asyncio
async def test_approve_changes_report_status_to_approved(fake_session) -> None:
    service, repositories = make_report_service(fake_session)

    report = SimpleNamespace(
        id=1,
        status="SUBMITTED",
        updated_at=None,
    )

    version = SimpleNamespace(
        id=2,
        version_number=2,
    )

    repositories["report"].get_by_id = AsyncMock(return_value=report)
    repositories["version"].get_latest = AsyncMock(return_value=version)
    repositories["review"].add = Mock()

    service.build_response = AsyncMock(return_value=SimpleNamespace())

    admin = SimpleNamespace(id=1, role="ADMIN")

    await service.approve_report(admin, 1)

    assert report.status == "APPROVED"

    review = repositories["review"].add.call_args.args[0]
    assert review.report_version_id == 2
    assert review.action == "APPROVE"


@pytest.mark.asyncio
async def test_manager_cannot_view_unsubmitted_version(fake_session) -> None:
    service, repositories = make_report_service(fake_session)

    report = SimpleNamespace(
        id=1,
        user_id=2,
        status="NEEDS_CORRECTION",
    )

    version_1 = SimpleNamespace(
        id=1,
        version_number=1,
        submitted_at=datetime(2026, 9, 6, 18, 57),
    )

    version_2 = SimpleNamespace(
        id=2,
        version_number=2,
        submitted_at=None,
    )

    repositories["report"].get_by_id = AsyncMock(return_value=report)
    repositories["version"].get_all = AsyncMock(return_value=[version_1, version_2])

    manager = SimpleNamespace(id=4, role="MANAGER")

    with pytest.raises(HTTPException) as exc:
        await service.get_version_detail(manager, 1, 2)

    assert exc.value.status_code == 403