import pytest
from sqlalchemy import text

from bot.repositories.stars_transactions_repository import PaymentsRepository


@pytest.mark.asyncio
async def test_insert_into_stars_transactions_success(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (
                    user_id,
                    role,
                    premium_until,
                    premium_plan,
                    free_attempts_left
                )
                VALUES (
                    :user_id,
                    :role,
                    :premium_until,
                    :premium_plan,
                    :free_attempts_left
                )
            """),
            {
                "user_id": 12345,
                "role": "normal",
                "premium_until": None,
                "premium_plan": None,
                "free_attempts_left": 5
            }
        )

    repo = PaymentsRepository(engine)

    await repo.insert_into_stars_transactions(
        user_id=12345,
        payload="premium_30",
        amount=100,
        charge_id="charge_123",
        product_type="premium",
        days=30
    )

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT
                    user_id,
                    payload,
                    amount,
                    charge_id,
                    status,
                    product_type
                FROM stars_transactions
                WHERE user_id = :user_id
            """),
            {"user_id": 12345}
        )

        transaction = result.mappings().fetchone()

        assert transaction["user_id"] == 12345
        assert transaction["payload"] == "premium_30"
        assert transaction["amount"] == 100
        assert transaction["charge_id"] == "charge_123"
        assert transaction["status"] == "success"
        assert transaction["product_type"] == "premium"

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT
                    role,
                    premium_plan,
                    free_attempts_left,
                    premium_until
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": 12345}
        )

        user = result.mappings().fetchone()

        assert user["role"] == "premium"
        assert user["premium_plan"] == "premium"
        assert user["free_attempts_left"] == 0
        assert user["premium_until"] is not None
