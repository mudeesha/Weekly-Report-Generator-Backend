from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException

from app.modules.users.schemas import UserInviteAcceptRequest, UserInviteRequest
from app.modules.users.service import UserService


@pytest.mark.asyncio
async def test_admin_can_create_manager_invitation(fake_session) -> None:
    repository = SimpleNamespace(get_by_email=AsyncMock(return_value=None))
    service = UserService(fake_session, repository)

    data = UserInviteRequest(
        name="Test Manager",
        email="manager@example.com",
        role="MANAGER",
    )

    result = await service.create_invitation(data)

    assert result.invitation_token
    assert result.expires_in_hours == 72


@pytest.mark.asyncio
async def test_invitation_creates_user_with_invited_role(fake_session) -> None:
    repository = SimpleNamespace(
        get_by_email=AsyncMock(return_value=None),
        add=Mock(),
    )

    service = UserService(fake_session, repository)

    invitation = await service.create_invitation(
        UserInviteRequest(
            name="Test Manager",
            email="manager@example.com",
            role="MANAGER",
        )
    )

    user = await service.accept_invitation(
        UserInviteAcceptRequest(
            token=invitation.invitation_token,
            password="Manager123",
        )
    )

    assert user.name == "Test Manager"
    assert user.email == "manager@example.com"
    assert user.role == "MANAGER"
    assert user.is_active is True
    repository.add.assert_called_once()


@pytest.mark.asyncio
async def test_invitation_cannot_be_accepted_twice(fake_session) -> None:
    repository = SimpleNamespace(
        get_by_email=AsyncMock(),
        add=Mock(),
    )

    repository.get_by_email.side_effect = [
        None,
        SimpleNamespace(id=5),
    ]

    service = UserService(fake_session, repository)

    invitation = await service.create_invitation(
        UserInviteRequest(
            name="Existing User",
            email="existing@example.com",
            role="TEAM_MEMBER",
        )
    )

    with pytest.raises(HTTPException) as exc:
        await service.accept_invitation(
            UserInviteAcceptRequest(
                token=invitation.invitation_token,
                password="Password123",
            )
        )

    assert exc.value.status_code == 409


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