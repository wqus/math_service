import pytest
from unittest.mock import AsyncMock
from bot.Filters.HasAttemptsLeftFilter import HasAttemptsLeft


@pytest.mark.asyncio
async def test_has_attempts_normal_user_success():
    message = AsyncMock()
    message.from_user.id = 123

    access_service = AsyncMock()
    access_service.get_user_role.return_value = "normal"
    access_service.has_attempts_left.return_value = True

    filter_res = HasAttemptsLeft()

    result = await filter_res(message, access_service)

    assert result is True


@pytest.mark.asyncio
async def test_has_attempts_normal_user_no_attempts():
    message = AsyncMock()
    message.from_user.id = 123

    access_service = AsyncMock()
    access_service.get_user_role.return_value = "normal"
    access_service.has_attempts_left.return_value = False

    filter_res = HasAttemptsLeft()

    result = await filter_res(message, access_service)

    assert result is False


@pytest.mark.asyncio
async def test_has_attempts_banned_user():
    message = AsyncMock()
    message.from_user.id = 123

    access_service = AsyncMock()
    access_service.get_user_role.return_value = "banned"

    filter_res = HasAttemptsLeft()

    result = await filter_res(message, access_service)

    assert result is False


@pytest.mark.asyncio
async def test_has_attempts_role_none():
    message = AsyncMock()
    message.from_user.id = 123

    access_service = AsyncMock()
    access_service.get_user_role.return_value = None

    filter_res = HasAttemptsLeft()

    result = await filter_res(message, access_service)

    assert result is False


@pytest.mark.asyncio
async def test_has_attempts_exception():
    message = AsyncMock()
    message.from_user.id = 123

    access_service = AsyncMock()
    access_service.get_user_role.return_value = "normal"

    access_service.has_attempts_left.side_effect = Exception()

    filter_ = HasAttemptsLeft()

    result = await filter_(message, access_service)

    assert result is False
