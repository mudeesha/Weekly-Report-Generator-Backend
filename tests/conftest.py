from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def fake_session():
    return SimpleNamespace(
        commit=AsyncMock(),
        refresh=AsyncMock(),
        flush=AsyncMock(),
        rollback=AsyncMock(),
    )