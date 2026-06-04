from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from bot.repositories.support_messages_repository import TicketRepository


@pytest.mark.asyncio
async def test_create_support_message_success(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO users (user_id, role, premium_until)
                VALUES (:user_id, :role, :premium)
            """),
            {
                "user_id": 12345,
                "role": "normal",
                "premium": None
            }
        )

    repo = TicketRepository(engine)

    ticket_id = await repo.create_support_message(
        12345,
        "Помогите пожалуйста"
    )

    assert ticket_id is not None

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT user_id, message, status
                FROM support_messages
                WHERE id = :id
            """),
            {"id": ticket_id}
        )

        ticket = result.mappings().fetchone()

        assert ticket["user_id"] == 12345
        assert ticket["message"] == "Помогите пожалуйста"
        assert ticket["status"] == "open"

@pytest.mark.asyncio
async def test_fetch_open_tickets_success(engine):
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
                INSERT INTO support_messages (
                    user_id,
                    message,
                    status
                )
                VALUES (
                    :user_id,
                    :message,
                    'open'
                )
            """),
            {
                "user_id": 12345,
                "message": "Тестовый тикет"
            }
        )

    repo = TicketRepository(engine)

    tickets = await repo.fetch_open_tickets()

    assert len(tickets) == 1
    assert tickets[0]["user_id"] == 12345
    assert tickets[0]["message"] == "Тестовый тикет"
    assert tickets[0]["status"] == "open"

@pytest.mark.asyncio
async def test_update_ticket_with_answer_success(engine):
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
                INSERT INTO users (user_id, role)
                VALUES (:user_id, :role)
            """),
            {
                "user_id": 777,
                "role": "admin"
            }
        )

        result = await conn.execute(
            text("""
                INSERT INTO support_messages (
                    user_id,
                    message
                )
                VALUES (
                    :user_id,
                    :message
                )
                RETURNING id
            """),
            {
                "user_id": 12345,
                "message": "Помогите"
            }
        )

        ticket_id = result.fetchone()[0]

    repo = TicketRepository(engine)

    await repo.update_ticket_with_answer(
        ticket_id=ticket_id,
        answer="Решение найдено",
        admin_id=777
    )

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT
                    status,
                    answer_message,
                    answered_by,
                    answered_at
                FROM support_messages
                WHERE id = :id
            """),
            {"id": ticket_id}
        )

        ticket = result.mappings().fetchone()

        assert ticket["status"] == "closed"
        assert ticket["answer_message"] == "Решение найдено"
        assert ticket["answered_by"] == 777
        assert ticket["answered_at"] is not None

@pytest.mark.asyncio
async def test_save_ticket_rating_success(engine):
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

        result = await conn.execute(
            text("""
                INSERT INTO support_messages (
                    user_id,
                    message
                )
                VALUES (
                    :user_id,
                    :message
                )
                RETURNING id
            """),
            {
                "user_id": 12345,
                "message": "Помогите"
            }
        )

        ticket_id = result.fetchone()[0]

    repo = TicketRepository(engine)

    result = await repo.save_ticket_rating(
        rating=5,
        ticket_id=ticket_id
    )

    assert result is True

    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT rating
                FROM support_messages
                WHERE id = :id
            """),
            {"id": ticket_id}
        )

        ticket = result.mappings().fetchone()

        assert ticket["rating"] == 5


@pytest.mark.asyncio
async def test_create_support_message_error():
    repo = TicketRepository(engine=AsyncMock())

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(side_effect=SQLAlchemyError("DB error"))
    repo.engine.begin = MagicMock(return_value=mock_ctx)

    with patch('bot.repositories.support_messages_repository.text'):
        with pytest.raises(SQLAlchemyError):
            await repo.create_support_message(123, "test")

@pytest.mark.asyncio
async def test_update_ticket_with_answer_error():
    repo = TicketRepository(engine=AsyncMock())

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(side_effect=SQLAlchemyError("DB error"))
    repo.engine.begin = MagicMock(return_value=mock_ctx)

    with patch('bot.repositories.support_messages_repository.text'):
        with pytest.raises(SQLAlchemyError):
            await repo.update_ticket_with_answer(123, "test", 321)


@pytest.mark.asyncio
async def test_update_ticket_with_answer_error():
    repo = TicketRepository(engine=AsyncMock())

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(side_effect=SQLAlchemyError("DB error"))
    repo.engine.begin = MagicMock(return_value=mock_ctx)

    with patch('bot.repositories.support_messages_repository.text'):
        with pytest.raises(SQLAlchemyError):
            await repo.update_ticket_with_answer(123, "test", 321)


@pytest.mark.asyncio
async def test_fetch_open_tickets_error():
    repo = TicketRepository(engine=AsyncMock())

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(side_effect=SQLAlchemyError("DB error"))
    repo.engine.begin = MagicMock(return_value=mock_ctx)

    with patch('bot.repositories.support_messages_repository.text'):
        with pytest.raises(SQLAlchemyError):
            await repo.fetch_open_tickets()