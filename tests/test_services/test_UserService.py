import pytest
from unittest.mock import AsyncMock
from sqlalchemy.exc import SQLAlchemyError
from bot.services.UserService import UserService


@pytest.mark.asyncio
async def test_init_user_success():
    repo = AsyncMock()
    service = UserService(repo)

    await service.init_user(12345)

    repo.create_user_if_not_exists.assert_called_once_with(12345)


@pytest.mark.asyncio
async def test_init_user_db_error():
    repo = AsyncMock()
    repo.create_user_if_not_exists.side_effect = SQLAlchemyError()
    service = UserService(repo)

    await service.init_user(12345)

    repo.create_user_if_not_exists.assert_called_once_with(12345)


@pytest.mark.asyncio
async def test_update_language_success():
    repo = AsyncMock()
    repo.update_user_language.return_value = True
    service = UserService(repo)

    result = await service.update_user_language(12345, "RU")

    assert result is True
    repo.update_user_language.assert_called_once_with(12345, "RU")


@pytest.mark.asyncio
async def test_update_language_db_error():
    repo = AsyncMock()
    repo.update_user_language.side_effect = SQLAlchemyError("DB error")
    service = UserService(repo)

    result = await service.update_user_language(12345, "RU")

    assert result is False
    repo.update_user_language.assert_called_once_with(12345, "RU")