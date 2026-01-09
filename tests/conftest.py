"""
Global fixtures for the pytest test suite.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="function")
def mock_session() -> AsyncMock:
    """
    Creates a mock of the SQLAlchemy AsyncSession using AsyncMock.
    This allows us to `await` methods like `commit` and `rollback`
    and use `assert_awaited_once` for verification.
    """
    session = AsyncMock(spec=AsyncSession)

    # Configure session.execute to return a MagicMock (synchronous result)
    # instead of an AsyncMock. This ensures that calling .scalars() on the
    # result does not return a coroutine.
    session.execute.return_value = MagicMock()

    return session
