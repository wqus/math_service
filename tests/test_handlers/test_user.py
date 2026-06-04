from datetime import datetime
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bot.handlers.user import handle_equation, handle_inequality, handle_expression, paginate_history, ai_functions, \
    generate_and_send_plot
from bot.core.ServiceResult import ServiceResult


@pytest.mark.asyncio
async def test_handle_equation_success():
    message = AsyncMock()
    message.text = "2x=4"
    message.from_user.id = 123
    user_language = "RU"
    texts = {"RU": {"show_solution": "Решение", "generate_similar": "Похожий", "error": "Ошибка: "}}
    history_service = AsyncMock()

    with patch('bot.handlers.user.solve_equation') as mock_solve, patch('bot.handlers.user.ai_functions_kb') as mock_kb:
        mock_solve.return_value = "x = 2"

        mock_kb.return_value = MagicMock()
        mock_kb.return_value.as_markup.return_value = "keyboard"

        await handle_equation(message, user_language, texts, history_service)

        mock_solve.assert_called_once_with("2x=4")
        message.answer.assert_called_once_with("x = 2", reply_markup="keyboard")
        history_service.save_message.assert_called_once_with(123, "2x=4", "x = 2")


@pytest.mark.asyncio
async def test_handle_equation_error():
    message = AsyncMock()
    message.text = "2x=4"
    user_language = "RU"
    texts = {"RU": {"error": "Ошибка: "}}
    history_service = AsyncMock()

    with patch('bot.handlers.user.solve_equation') as mock_solve:
        mock_solve.side_effect = ValueError("Invalid equation")

        await handle_equation(message, user_language, texts, history_service)

        message.answer.assert_called_once_with("Ошибка: Invalid equation")
        history_service.save_message.assert_not_called()


@pytest.mark.asyncio
async def test_handle_inequality_success():
    message = AsyncMock()
    message.text = "x>2"
    message.from_user.id = 123
    user_language = "RU"
    texts = {"RU": {"show_solution": "Решение", "generate_similar": "Похожий", "error": "Ошибка: "}}
    history_service = AsyncMock()

    with patch('bot.handlers.user.solve_inequality') as mock_solve, patch(
            'bot.handlers.user.ai_functions_kb') as mock_kb:
        mock_solve.return_value = "x > 2"
        mock_kb.return_value = MagicMock()
        mock_kb.return_value.as_markup.return_value = "keyboard"

        await handle_inequality(message, user_language, texts, history_service)

        mock_solve.assert_called_once_with("x>2")
        message.answer.assert_called_once()
        history_service.save_message.assert_called_once_with(123, "x>2", "x > 2")


@pytest.mark.asyncio
async def test_handle_expression_success():
    message = AsyncMock()
    message.text = "2 + 2"
    message.from_user.id = 123

    history_service = AsyncMock()

    with patch('bot.handlers.user.ai_functions_kb') as mock_kb:
        mock_keyboard = MagicMock()
        mock_keyboard.as_markup.return_value = "keyboard_markup"
        mock_kb.return_value = mock_keyboard

        await handle_expression(
            message=message,
            user_language="ru",
            texts={"ru": {"show_solution": "Показать решение", "generate_similar": "Сгенерировать похожее",
                          "error": "Ошибка: "}},
            history_service=history_service
        )

        message.answer.assert_awaited_once_with("4", reply_markup="keyboard_markup")

        history_service.save_message.assert_awaited_once_with(123, "2 + 2", "4")


@pytest.mark.asyncio
async def test_paginate_history_success():
    callback = AsyncMock()
    callback.data = "user:history:next:123|2026-01-01T12:00:00"
    callback.from_user.id = 456
    callback.message = AsyncMock()
    callback.answer = AsyncMock()

    history_service = AsyncMock()
    mock_result = ServiceResult(
        success=True,
        message_key="history_answer",
        data={
            'rows': [("2 + 2 = 4", datetime.now(), 1)],
            'prev_cursor': None,
            'next_cursor': (124, datetime.now())
        }
    )
    history_service.get_user_history.return_value = mock_result
    with patch('bot.handlers.user.format_history_list') as mock_format:
        mock_format.return_value = ('formatted_text', None)

        await paginate_history(
            callback=callback,
            texts={},
            history_service=history_service,
            user_language="RU"
        )

        history_service.get_user_history.assert_called_once()
        call_args = history_service.get_user_history.call_args[1]
        assert call_args['direction'] == "next"

        callback.message.edit_text.assert_called_once()
        callback.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_ai_functions_show_solution():
    callback = AsyncMock()
    callback.data = "ai:show_solution:2+2"
    callback.message = AsyncMock()
    callback.answer = AsyncMock()

    ai_service = AsyncMock()
    mock_result = AsyncMock()
    mock_result.success = True
    mock_result.data = {"response": "4"}
    ai_service.get_show_solution.return_value = mock_result

    texts = {"RU": {"send_solution": "Решение: {solution}"}}

    await ai_functions(callback, ai_service, texts, "RU")

    callback.message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_ai_functions_generate_similar():
    callback = AsyncMock()
    callback.data = "ai:generate_similar:2+2"
    callback.message = AsyncMock()
    callback.answer = AsyncMock()

    ai_service = AsyncMock()
    mock_result = AsyncMock()
    mock_result.success = True
    mock_result.data = {"response": "3+3"}
    ai_service.get_generate_similar.return_value = mock_result

    texts = {"RU": {"send_similar": "Похожее выражение на `{expression}`: {similar}"}}

    await ai_functions(callback, ai_service, texts, "RU")

    callback.message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_show_user_history_success():
    message = AsyncMock()
    message.from_user.id = 123
    message.answer = AsyncMock()

    history_service = AsyncMock()
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.data = {
        'rows': [("2+2=4", "2026-01-01", 1)],
        'prev_cursor': None,
        'next_cursor': None
    }
    history_service.get_user_history.return_value = mock_result

    texts = {"RU": {"history_error": "Ошибка"}}

    with patch('bot.handlers.user.format_history_list') as mock_format:
        mock_format.return_value = ("отформатированный текст", None)

        from bot.handlers.user import show_user_history
        await show_user_history(
            message=message,
            texts=texts,
            history_service=history_service,
            user_language="RU"
        )

        message.answer.assert_called_once()
        history_service.get_user_history.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_generate_and_send_plot_success():
    message = AsyncMock()
    message.text = "x**2"
    message.from_user.id = 123
    message.answer_photo = AsyncMock()
    message.answer = AsyncMock()

    state = AsyncMock()
    state.clear = AsyncMock()

    access_service = AsyncMock()
    access_service.decrease_attempts.return_value = 5

    history_service = AsyncMock()

    texts = {
        "RU": {
            "plot_caption": "График функции {0}",
            "attempts_ended": "Попытки кончились",
            "plot_try_again": "Ошибка при создании графика"
        }
    }

    with patch('bot.handlers.user.to_numpy_function') as mock_tonumpy, patch(
            'bot.handlers.user.generate_plot') as mock_plot, patch('bot.handlers.user.kb_info') as mock_kb:
        mock_tonumpy.return_value = lambda x: x
        mock_plot.return_value = MagicMock()
        mock_plot.return_value.read.return_value = b"image_data"
        mock_kb.return_value = "keyboard"

        await generate_and_send_plot(
            message=message,
            state=state,
            user_language="RU",
            texts=texts,
            access_service=access_service,
            history_service=history_service
        )

        message.answer_photo.assert_called_once()
        history_service.save_message.assert_called_once()
        state.clear.assert_called_once()
        access_service.decrease_attempts.assert_called_once_with(123)
