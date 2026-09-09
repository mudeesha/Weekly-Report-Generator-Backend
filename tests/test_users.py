from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
import pytest
from fastapi import HTTPException
from app.modules.users.service import UserService

@pytest.mark.asyncio
async def test_admin_cannot_deactivate_self(fake_session) -> None:
    admin = SimpleNamespace(id=1, is_active=True)
    repository = SimpleNamespace(get_by_id=AsyncMock(return_value=admin))
    service = UserService(fake_session, repository)

    with pytest.raises(HTTPException) as exc:
        await service.deactivate(admin, 1)

    assert exc.value.status_code == 409
    assert admin.is_active is True


@pytest.mark.asyncio
async def test_admin_can_deactivate_other_user(fake_session) -> None:
    admin = SimpleNamespace(id=1)
    member = SimpleNamespace(id=2, is_active=True)

    repository = SimpleNamespace(get_by_id=AsyncMock(return_value=member))
    service = UserService(fake_session, repository)

    result = await service.deactivate(admin, 2)

    assert result.is_active is False
    fake_session.commit.assert_awaited_once()