import pytest
from sqlalchemy import text

from bot.repositories.history_repository import HistoryRepository


@pytest.mark.asyncio
async def test_create_message_record_success(engine):
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

    repo = HistoryRepository(engine)

    await repo.create_message_record(
        12345,
        "2+2",
        "4"
    )

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT user_id, input_message, output_message
                FROM history
                WHERE user_id = :user_id
            """),
            {"user_id": 12345}
        )

        row = result.mappings().fetchone()

        assert row["user_id"] == 12345
        assert row["input_message"] == "2+2"
        assert row["output_message"] == "4"


@pytest.mark.asyncio
async def test_fetch_user_history_success(engine):
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

        await conn.execute(
            text("""
                INSERT INTO history
                (user_id, input_message, output_message)
                VALUES
                (:user_id, '1+1', '2'),
                (:user_id, '2+2', '4')
            """),
            {"user_id": 12345}
        )

    repo = HistoryRepository(engine)

    result = await repo.fetch_user_history(12345)

    assert len(result) == 2

    assert result[0]["input_message"] == "2+2"
    assert result[0]["output_message"] == "4"


@pytest.mark.asyncio
async def test_has_newer_records_success(engine):
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

        await conn.execute(
            text("""
                INSERT INTO history
                (user_id, input_message, output_message)
                VALUES
                (:user_id, 'old', 'old'),
                (:user_id, 'new', 'new')
            """),
            {"user_id": 12345}
        )

        result = await conn.execute(
            text("""
                SELECT id, created_at
                FROM history
                ORDER BY id
                LIMIT 1
            """)
        )

        first_record = result.mappings().fetchone()

    repo = HistoryRepository(engine)

    has_newer = await repo.has_newer_records(
        12345,
        first_record["created_at"],
        first_record["id"]
    )

    assert has_newer is True


@pytest.mark.asyncio
async def test_has_older_records_success(engine):
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

        await conn.execute(
            text("""
                INSERT INTO history
                (user_id, input_message, output_message)
                VALUES
                (:user_id, 'old', 'old'),
                (:user_id, 'new', 'new')
            """),
            {"user_id": 12345}
        )

        result = await conn.execute(
            text("""
                SELECT id, created_at
                FROM history
                ORDER BY id DESC
                LIMIT 1
            """)
        )

        last_record = result.mappings().fetchone()

    repo = HistoryRepository(engine)

    has_older = await repo.has_older_records(
        12345,
        last_record["created_at"],
        last_record["id"]
    )

    assert has_older is True
