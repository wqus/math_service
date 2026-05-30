import pytest
from sqlalchemy import text

from bot.repositories.users_repository import UserRepository


@pytest.mark.asyncio
async def test_create_user_if_not_exists_success(engine):
    repo = UserRepository(engine)

    result = await repo.create_user_if_not_exists(12345)

    assert result is True

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT user_id, role
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": 12345}
        )

        user = result.mappings().fetchone()

        assert user["user_id"] == 12345
        assert user["role"] == "normal"


@pytest.mark.asyncio
async def test_create_user_if_not_exists_already_exists(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (user_id, role)
                VALUES (:user_id, :role)
            """),
            {
                "user_id": 12345,
                "role": "normal"
            }
        )

    repo = UserRepository(engine)

    result = await repo.create_user_if_not_exists(12345)

    assert result is False


@pytest.mark.asyncio
async def test_update_user_language_success(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (user_id, role, language)
                VALUES (:user_id, :role, :language)
            """),
            {
                "user_id": 12345,
                "role": "normal",
                "language": "EN"
            }
        )

    repo = UserRepository(engine)

    result = await repo.update_user_language(
        12345,
        "RU"
    )

    assert result is True

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT language
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": 12345}
        )

        user = result.mappings().fetchone()

        assert user["language"] == "RU"


@pytest.mark.asyncio
async def test_fetch_user_access_success(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (
                    user_id,
                    role,
                    premium_until
                )
                VALUES (
                    :user_id,
                    :role,
                    NOW() + INTERVAL '30 days'
                )
            """),
            {
                "user_id": 12345,
                "role": "premium"
            }
        )

    repo = UserRepository(engine)

    premium_until, role = await repo.fetch_user_access(
        12345
    )

    assert role == "premium"
    assert premium_until is not None


@pytest.mark.asyncio
async def test_fetch_user_access_expired_premium(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (
                    user_id,
                    role,
                    premium_until
                )
                VALUES (
                    :user_id,
                    :role,
                    NOW() - INTERVAL '1 day'
                )
            """),
            {
                "user_id": 12345,
                "role": "premium"
            }
        )

    repo = UserRepository(engine)

    premium_until, role = await repo.fetch_user_access(
        12345
    )

    assert premium_until is None
    assert role == "normal"


@pytest.mark.asyncio
async def test_check_and_reset_attempts_success(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (
                    user_id,
                    role,
                    free_attempts_left,
                    free_attempts_reset
                )
                VALUES (
                    :user_id,
                    :role,
                    0,
                    NOW() - INTERVAL '1 minute'
                )
            """),
            {
                "user_id": 12345,
                "role": "normal"
            }
        )

    repo = UserRepository(engine)

    attempts = await repo.check_and_reset_attempts(
        12345
    )

    assert attempts == 5


@pytest.mark.asyncio
async def test_decrease_attempts_success(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (
                    user_id,
                    role,
                    free_attempts_left
                )
                VALUES (
                    :user_id,
                    :role,
                    5
                )
            """),
            {
                "user_id": 12345,
                "role": "normal"
            }
        )

    repo = UserRepository(engine)

    attempts = await repo.decrease_attempts(
        12345
    )

    assert attempts == 4

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT free_attempts_left
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": 12345}
        )

        user = result.mappings().fetchone()

        assert user["free_attempts_left"] == 4
