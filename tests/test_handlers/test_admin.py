import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bot.handlers.admin import handle_tickets_command, process_ticket_answer, handle_ticket_admin_callback, \
    handle_add_admin_command, handle_remove_admin_command, handle_ban_user_command, handle_bans_history_command, \
    handle_unban_user_callback, handle_load_bans_callback
from bot.core.ServiceResult import ServiceResult


@pytest.mark.asyncio
async def test_handle_load_bans_callback_success():
    callback = MagicMock()
    callback.data = "bans:load:10"
    callback.message.answer = AsyncMock()
    callback.answer = AsyncMock()

    admin_service = AsyncMock()
    admin_service.fetch_bans.return_value = ServiceResult(
        success=True,
        message_key="bans_loaded",
        data={"last_ban_id": 1, "has_more": False},
    )

    with patch("bot.handlers.admin.send_bans", new=AsyncMock()):
        await handle_load_bans_callback(
            callback,
            "ru",
            {"ru": {"bans_loaded": "ok"}},
            admin_service,
        )

    callback.message.answer.assert_awaited_once()
    callback.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_bans_history_command_success():
    message = MagicMock()
    message.answer = AsyncMock()

    admin_service = AsyncMock()
    admin_service.fetch_bans.return_value = ServiceResult(
        success=True,
        message_key="bans_loaded",
        data={
            "bans": ["ban"],
            "last_ban_id": 1,
            "has_more": False,
        },
    )

    with patch("bot.handlers.admin.send_bans", new=AsyncMock()):
        await handle_bans_history_command(
            message=message,
            user_language="ru",
            texts={"ru": {"bans_loaded": "Баны загружены"}},
            admin_service=admin_service,
        )

    admin_service.fetch_bans.assert_awaited_once()
    message.answer.assert_awaited_once_with(
        text="Баны загружены",
        reply_markup=None,
    )


@pytest.mark.asyncio
async def test_handle_tickets_command():
    message = AsyncMock()

    admin_service = AsyncMock()
    admin_service.fetch_tickets.return_value = ServiceResult(
        success=True,
        message_key="tickets_loaded",
        data={
            "last_ticket_id": 10,
            "has_more": True,
        }
    )

    kb = MagicMock()
    kb.as_markup.return_value = "markup"

    with (
        patch("bot.handlers.admin.send_tickets", new=AsyncMock()),
        patch(
            "bot.handlers.admin.load_three_tickets_kb",
            new=AsyncMock(return_value=kb)
        )
    ):
        await handle_tickets_command(
            message=message,
            user_language="ru",
            texts={"ru": {"tickets_loaded": "Тикеты загружены"}},
            admin_service=admin_service,
        )

    admin_service.fetch_tickets.assert_awaited_once()

    message.answer.assert_awaited_once_with(
        text="Тикеты загружены",
        reply_markup="markup",
    )


@pytest.mark.asyncio
async def test_admin_callback_load_success():
    callback = AsyncMock()
    callback.data = "admin:load:10"
    callback.message.answer = AsyncMock()
    callback.answer = AsyncMock()

    admin_service = AsyncMock()
    admin_service.fetch_tickets.return_value = ServiceResult(
        success=True,
        message_key="tickets_loaded",
        data={"last_ticket_id": 20, "has_more": True}
    )

    with patch("bot.handlers.admin.send_tickets", new=AsyncMock()), \
         patch("bot.handlers.admin.load_three_tickets_kb", return_value=MagicMock()):

        await handle_ticket_admin_callback(
            callback=callback,
            state=AsyncMock(),
            user_language="ru",
            texts={"ru": {"tickets_loaded": "ok"}},
            admin_service=admin_service,
        )

    admin_service.fetch_tickets.assert_awaited_once_with(current_position=10)
    callback.message.answer.assert_awaited_once()
    callback.answer.assert_awaited_once()

@pytest.mark.asyncio
async def test_process_ticket_answer_success():
    message = AsyncMock()
    message.text = "my answer"
    message.from_user.id = 123

    state = AsyncMock()
    state.get_data.return_value = {
        "ticket_message_id": 10,
        "ticket_id": "1",
        "ticket_user_id": 999,
    }

    bot = AsyncMock()

    admin_service = AsyncMock()
    admin_service.save_support_answer.return_value = ServiceResult(
        success=True,
        message_key="answer_saved"
    )

    kb = MagicMock()
    kb.as_markup.return_value = "markup"

    with patch(
        "bot.handlers.admin.rate_support_answer_kb",
        new=AsyncMock(return_value=kb)
    ):
        await process_ticket_answer(
            message=message,
            state=state,
            user_language="ru",
            texts={"ru": {
                "support_answer": "Ответ: {answer}",
                "answer_saved": "ok"
            }},
            bot=bot,
            admin_service=admin_service,
        )

    admin_service.save_support_answer.assert_awaited_once_with(1, "my answer", 123)

    bot.send_message.assert_awaited_once()
    message.answer.assert_awaited_once_with(text="ok")
    state.clear.assert_awaited_once()

