from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.modules.auth.security import create_access_token, decode_access_token, hash_password, require_roles
from app.modules.auth.service import AuthService


def test_access_token_contains_user_id() -> None:
    token = create_access_token(25)
    payload = decode_access_token(token)

    assert payload["sub"] == "25"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_admin_role_is_allowed() -> None:
    checker = require_roles("ADMIN")
    user = SimpleNamespace(role="ADMIN")

    result = await checker(user)

    assert result is user


@pytest.mark.asyncio
async def test_manager_cannot_use_admin_only_action() -> None:
    checker = require_roles("ADMIN")
    user = SimpleNamespace(role="MANAGER")

    with pytest.raises(HTTPException) as exc:
        await checker(user)

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_inactive_user_cannot_authenticate() -> None:
    user = SimpleNamespace(
        id=10,
        email="inactive@example.com",
        password_hash=hash_password("Password123"),
        is_active=False,
    )

    repository = SimpleNamespace(get_by_email=AsyncMock(return_value=user))
    service = AuthService(repository)

    with pytest.raises(HTTPException) as exc:
        await service.authenticate("inactive@example.com", "Password123")

    assert exc.value.status_code == 403
    assert exc.value.detail == "This account is inactive."


@pytest.mark.asyncio
async def test_wrong_password_returns_none() -> None:
    user = SimpleNamespace(
        id=10,
        email="user@example.com",
        password_hash=hash_password("Password123"),
        is_active=True,
    )

    repository = SimpleNamespace(get_by_email=AsyncMock(return_value=user))
    service = AuthService(repository)

    result = await service.authenticate("user@example.com", "WrongPassword")

    assert result is None