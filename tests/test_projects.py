from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.modules.projects.service import ProjectService


@pytest.mark.asyncio
async def test_project_with_report_history_cannot_be_deleted(fake_session) -> None:
    project = SimpleNamespace(id=1, name="Weekly Report System")

    project_repository = SimpleNamespace(
        get_by_id=AsyncMock(return_value=project),
        is_used_in_reports=AsyncMock(return_value=True),
        delete=AsyncMock(),
    )

    user_repository = SimpleNamespace()
    service = ProjectService(fake_session, project_repository, user_repository)

    with pytest.raises(HTTPException) as exc:
        await service.delete(1)

    assert exc.value.status_code == 409
    project_repository.delete.assert_not_awaited()
    fake_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_unused_project_can_be_deleted(fake_session) -> None:
    project = SimpleNamespace(id=2, name="Unused Project")

    project_repository = SimpleNamespace(
        get_by_id=AsyncMock(return_value=project),
        is_used_in_reports=AsyncMock(return_value=False),
        delete=AsyncMock(),
    )

    user_repository = SimpleNamespace()
    service = ProjectService(fake_session, project_repository, user_repository)

    await service.delete(2)

    project_repository.delete.assert_awaited_once_with(project)
    fake_session.commit.assert_awaited_once()