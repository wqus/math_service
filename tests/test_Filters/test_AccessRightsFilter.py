import pytest
from unittest.mock import AsyncMock
from bot.Filters.AccessRightsFilter import AccessRightsFilter


@pytest.mark.asyncio
async def test_access_rights_normal_user():
    message = AsyncMock()
    message.from_user.id = 123

    access_service = AsyncMock()
    access_service.get_user_role.return_value = "normal"

    filter_res = AccessRightsFilter(0)

    result = await filter_res(message, access_service)

    assert result is True


@pytest.mark.asyncio
async def test_access_rights_premium_user():
    message = AsyncMock()
    message.from_user.id = 123

    access_service = AsyncMock()
    access_service.get_user_role.return_value = "premium"

    filter_res = AccessRightsFilter(1)

    result = await filter_res(message, access_service)

    assert result is True


@pytest.mark.asyncio
async def test_access_rights_admin_not_owner():
    message = AsyncMock()
    message.from_user.id = 123

    access_service = AsyncMock()
    access_service.get_user_role.return_value = "admin"

    filter_res = AccessRightsFilter(3)

    result = await filter_res(message, access_service)

    assert result is False


@pytest.mark.asyncio
async def test_access_rights_role_none():
    message = AsyncMock()
    message.from_user.id = 123

    access_service = AsyncMock()
    access_service.get_user_role.return_value = None

    filter_res = AccessRightsFilter(0)

    result = await filter_res(message, access_service)

    assert result is False


@pytest.mark.asyncio
async def test_access_rights_unknown_role():
    message = AsyncMock()
    message.from_user.id = 123

    access_service = AsyncMock()
    access_service.get_user_role.return_value = "superman"

    filter_res = AccessRightsFilter(0)

    result = await filter_res(message, access_service)

    assert result is False
