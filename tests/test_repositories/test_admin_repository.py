import pytest
from sqlalchemy import text
from bot.repositories.admins_repository import AdminRepository


@pytest.mark.asyncio
async def test_add_admin_success(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (user_id, role, premium_until)
                VALUES (:user_id, :role, :premium)
            """),
            {"user_id": 12345, "role": "normal", "premium": None}
        )

    repo = AdminRepository(engine)
    await repo.add_admin(12345)

    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT role FROM users WHERE user_id = :user_id"),
            {"user_id": 12345}
        )
        row = result.fetchone()
        assert row[0] == "admin"


@pytest.mark.asyncio
async def test_remove_admin_success(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (user_id, role, premium_until)
                VALUES (:user_id, :role, NOW() + INTERVAL '30 days')
            """),
            {"user_id": 12345, "role": "admin"}
        )

    repo = AdminRepository(engine)
    await repo.remove_admin(12345)

    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT role FROM users WHERE user_id = :user_id"),
            {"user_id": 12345}
        )
        row = result.fetchone()
        assert row[0] == "premium"