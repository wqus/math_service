from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from bot.repositories.banned_users_repository import BannedRepository


@pytest.mark.asyncio
async def test_fetch_bans_success(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (user_id, role, premium_until)
                VALUES (:user_id, :role, :premium)
            """),
            {"user_id": 12345, "role": "normal", "premium": None}
        )

        await conn.execute(
            text("""
                INSERT INTO users (user_id, role, premium_until)
                VALUES (:user_id, :role, :premium)
            """),
            {"user_id": 123, "role": "admin", "premium": None}
        )

        await conn.execute(
            text("""
                INSERT INTO banned_users (user_id, banned_by, banned_at, reason, active)
                VALUES (:user_id, :banned_by, NOW(), :reason, :active)
            """),
            {"user_id": 12345, "banned_by": 123, "reason": "spam", "active": True}
        )

    repo = BannedRepository(engine)
    result = await repo.fetch_bans()

    assert len(result) == 1
    assert result[0]["user_id"] == 12345
    assert result[0]["banned_by"] == 123
    assert result[0]["reason"] == "spam"


@pytest.mark.asyncio
async def test_ban_user_success(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (user_id, role, premium_until)
                VALUES (:user_id, :role, :premium)
            """),
            {"user_id": 12345, "role": "normal", "premium": None}
        )

        await conn.execute(
            text("""
                INSERT INTO users (user_id, role, premium_until)
                VALUES (:user_id, :role, :premium)
            """),
            {"user_id": 123, "role": "admin", "premium": None}
        )

    repo = BannedRepository(engine)
    await repo.ban_user(12345, 123, "spam")

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT user_id, banned_by, reason, active
                FROM banned_users
                WHERE user_id = :user_id
            """),
            {"user_id": 12345}
        )

        row = result.mappings().fetchone()

        assert row["user_id"] == 12345
        assert row["banned_by"] == 123
        assert row["reason"] == "spam"
        assert row["active"] is True


@pytest.mark.asyncio
async def test_unban_user_success(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (user_id, role, role_before_ban)
                VALUES (:user_id, :role, :role_before_ban)
            """),
            {
                "user_id": 12345,
                "role": "banned",
                "role_before_ban": "admin"
            }
        )
        await conn.execute(
            text("""
                INSERT INTO users (user_id, role, premium_until)
                VALUES (:user_id, :role, :premium)
            """),
            {"user_id": 123, "role": "admin", "premium": None}
        )

        await conn.execute(
            text("""
                INSERT INTO banned_users (user_id, banned_by, banned_at, reason, active)
                VALUES (:user_id, :banned_by, NOW(), :reason, :active)
            """),
            {
                "user_id": 12345,
                "banned_by": 123,
                "reason": "spam",
                "active": True
            }
        )

    repo = BannedRepository(engine)
    await repo.unban_user(12345)

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT user_id, role, role_before_ban
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": 12345}
        )

        user = result.mappings().fetchone()

        assert user["user_id"] == 12345
        assert user["role"] == "admin"
        assert user["role_before_ban"] is None

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT active
                FROM banned_users
                WHERE user_id = :user_id
            """),
            {"user_id": 12345}
        )

        ban = result.mappings().fetchone()

        assert ban["active"] is False


@pytest.mark.asyncio
async def test_ban_user_error():
    repo = BannedRepository(engine=AsyncMock())

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(side_effect=SQLAlchemyError("DB error"))
    repo.engine.begin = MagicMock(return_value=mock_ctx)

    with patch('bot.repositories.banned_users_repository.text'):
        with pytest.raises(SQLAlchemyError):
            await repo.ban_user(1, 2, 'reason')


@pytest.mark.asyncio
async def test_unban_user_error():
    repo = BannedRepository(engine=AsyncMock())

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(side_effect=SQLAlchemyError("DB error"))
    repo.engine.begin = MagicMock(return_value=mock_ctx)

    with patch('bot.repositories.banned_users_repository.text'):
        with pytest.raises(SQLAlchemyError):
            await repo.unban_user(1)
