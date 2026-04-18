import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

from sqlalchemy.exc import SQLAlchemyError

from bot.services.AccessService import AccessService


@pytest.mark.asyncio
async def test_get_user_role_valid_cache():
    user_id = 1
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    cached_data = {
        'role': 'premium',
        'premium_until': future_date.isoformat()
    }
    mock_cache = AsyncMock()
    mock_cache.get_access_data.return_value = cached_data

    service = AccessService(
        users_repo=AsyncMock(),
        ban_repo=AsyncMock(),
        admins_repo=AsyncMock(),
        cache=mock_cache,
    )

    role = await service.get_user_role(user_id)

    assert role == 'premium'
    mock_cache.get_access_data.assert_called_once_with(user_id)
    service.users_repo.fetch_user_access.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_role_invalid_cache():
    user_id = 1
    date = datetime.now(timezone.utc) - timedelta(days=1)
    cached_data = {
        'role': 'premium',
        'premium_until': date.isoformat()
    }

    mock_cache = AsyncMock()
    mock_users_repo = AsyncMock()

    mock_cache.get_access_data.return_value = cached_data
    mock_cache.set_access_data.return_value = True

    new_date = datetime.now(timezone.utc) + timedelta(days=1)
    mock_users_repo.fetch_user_access.return_value = new_date, 'premium'

    service = AccessService(
        users_repo=mock_users_repo,
        ban_repo=AsyncMock(),
        admins_repo=AsyncMock(),
        cache=mock_cache,
    )

    role = await service.get_user_role(user_id)

    assert role == 'premium'
    mock_cache.get_access_data.assert_called_once_with(user_id)
    mock_users_repo.fetch_user_access.assert_called_once_with(user_id)
    mock_cache.set_access_data.assert_called_once_with(user_id, 'premium', str(new_date))


@pytest.mark.asyncio
async def test_has_attempts_left_valid_cache():
    user_id = 1

    mock_cache = AsyncMock()
    mock_cache.get_attempts.return_value = '5'

    service = AccessService(
        users_repo=AsyncMock(),
        ban_repo=AsyncMock(),
        admins_repo=AsyncMock(),
        cache=mock_cache,
    )

    result = await service.has_attempts_left(user_id)

    assert result == True
    mock_cache.get_attempts.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_has_attempts_left_invalid_cache():
    user_id = 1

    mock_cache = AsyncMock()
    mock_users_repo = AsyncMock()

    mock_cache.get_attempts.return_value = None
    mock_cache.set_attempts.return_value = True
    mock_users_repo.check_and_reset_attempts.return_value = 5

    service = AccessService(
        users_repo=mock_users_repo,
        ban_repo=AsyncMock(),
        admins_repo=AsyncMock(),
        cache=mock_cache,
    )
    result = await service.has_attempts_left(user_id)

    assert result == True
    mock_cache.get_attempts.assert_called_once_with(user_id)
    mock_cache.set_attempts.assert_called_once_with(user_id, 5)
    mock_users_repo.check_and_reset_attempts.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_decrease_attempts():
    user_id = 1

    mock_cache = AsyncMock()
    mock_users_repo = AsyncMock()

    mock_users_repo.decrease_attempts.return_value = 4
    mock_cache.set_attempts.return_value = True
    service = AccessService(
        users_repo=mock_users_repo,
        ban_repo=AsyncMock(),
        admins_repo=AsyncMock(),
        cache=mock_cache,
    )

    attempts = await service.decrease_attempts(user_id)

    assert attempts == 4
    mock_users_repo.decrease_attempts.assert_called_once_with(user_id)
    mock_cache.set_attempts.assert_called_once_with(user_id, 4)


@pytest.mark.asyncio
async def test_ban_user_success():
    mock_ban_repo = AsyncMock()
    mock_cache = AsyncMock()

    service = AccessService(
        users_repo=AsyncMock(),
        ban_repo=mock_ban_repo,
        admins_repo=AsyncMock(),
        cache=mock_cache,
    )

    result = await service.ban_user(user_id=1, admin_id=2, reason="спам")

    assert result.success == True
    assert result.message_key == "user_was_banned_successful"
    mock_ban_repo.ban_user.assert_called_once_with(1, 2, "спам")
    mock_cache.invalidate_access.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_ban_user_db_error():
    mock_ban_repo = AsyncMock()
    mock_ban_repo.ban_user.side_effect = SQLAlchemyError()

    service = AccessService(
        users_repo=AsyncMock(),
        ban_repo=mock_ban_repo,
        admins_repo=AsyncMock(),
        cache=AsyncMock(),
    )

    result = await service.ban_user(1, 2, "спам")

    assert result.success == False
    assert result.message_key == "user_was_banned_unsuccessful"


@pytest.mark.asyncio
async def test_unban_user_success():
    mock_ban_repo = AsyncMock()
    mock_cache = AsyncMock()

    service = AccessService(
        users_repo=AsyncMock(),
        ban_repo=mock_ban_repo,
        admins_repo=AsyncMock(),
        cache=mock_cache,
    )

    result = await service.unban_user(user_id=1)

    assert result.success == True
    assert result.message_key == "successful_unban"
    mock_ban_repo.unban_user.assert_called_once_with(1)
    mock_cache.invalidate_access.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_unban_user_db_error():
    mock_ban_repo = AsyncMock()
    mock_ban_repo.unban_user.side_effect = SQLAlchemyError()

    service = AccessService(
        users_repo=AsyncMock(),
        ban_repo=mock_ban_repo,
        admins_repo=AsyncMock(),
        cache=AsyncMock(),
    )

    result = await service.unban_user(1)

    assert result.success == False
    assert result.message_key == "unsuccessful_unban"


@pytest.mark.asyncio
async def test_assign_admin_success():
    mock_admins_repo = AsyncMock()
    mock_cache = AsyncMock()

    service = AccessService(
        users_repo=AsyncMock(),
        ban_repo=AsyncMock(),
        admins_repo=mock_admins_repo,
        cache=mock_cache,
    )

    result = await service.assign_admin(user_id=123)

    assert result.success == True
    assert result.message_key == "add_admin_successful"
    mock_admins_repo.add_admin.assert_called_once_with(123)
    mock_cache.invalidate_access.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_assign_admin_db_error():
    mock_admins_repo = AsyncMock()
    mock_admins_repo.add_admin.side_effect = SQLAlchemyError()

    service = AccessService(
        users_repo=AsyncMock(),
        ban_repo=AsyncMock(),
        admins_repo=mock_admins_repo,
        cache=AsyncMock(),
    )

    result = await service.assign_admin(user_id=123)

    assert result.success == False
    assert result.message_key == "add_admin_unsuccessful"
    mock_admins_repo.add_admin.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_remove_admin_success():
    mock_admins_repo = AsyncMock()
    mock_cache = AsyncMock()

    service = AccessService(
        users_repo=AsyncMock(),
        ban_repo=AsyncMock(),
        admins_repo=mock_admins_repo,
        cache=mock_cache,
    )

    result = await service.remove_admin(user_id=123)

    assert result.success == True
    assert result.message_key == "remove_admin_successful"
    mock_admins_repo.remove_admin.assert_called_once_with(123)
    mock_cache.invalidate_access.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_remove_admin_db_error():
    mock_admins_repo = AsyncMock()
    mock_admins_repo.remove_admin.side_effect = SQLAlchemyError()

    service = AccessService(
        users_repo=AsyncMock(),
        ban_repo=AsyncMock(),
        admins_repo=mock_admins_repo,
        cache=AsyncMock(),
    )
    result = await service.remove_admin(user_id=1)

    assert result.success == False

    assert result.message_key == 'remove_admin_unsuccessful'
    mock_admins_repo.remove_admin.assert_called_once_with(1)
