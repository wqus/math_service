import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from bot.handlers.user import handle_equation, handle_inequality, handle_expression


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
async def test_handle_expression_success():
    message = AsyncMock()
    message.text = "2+2"
    message.from_user.id = 123
    user_language = "RU"
    texts = {"RU": {"show_solution": "Решение", "generate_similar": "Похожий", "error": "Ошибка: "}}
    history_service = AsyncMock()

    with patch('bot.handlers.user.evaluate_expression') as mock_eval, patch('bot.handlers.user.ai_functions_kb') as mock_kb:
        mock_eval.return_value = "4"

        mock_kb.return_value = MagicMock()
        mock_kb.return_value.as_markup.return_value = "keyboard"

        await handle_expression(message, user_language, texts, history_service)

        mock_eval.assert_called_once_with("2+2")
        message.answer.assert_called_once_with("4", reply_markup="keyboard")


@pytest.mark.asyncio
async def test_handle_inequality_success():
    message = AsyncMock()
    message.text = "x>2"
    message.from_user.id = 123
    user_language = "RU"
    texts = {"RU": {"show_solution": "Решение", "generate_similar": "Похожий", "error": "Ошибка: "}}
    history_service = AsyncMock()

    with patch('bot.handlers.user.solve_inequality') as mock_solve, patch('bot.handlers.user.ai_functions_kb') as mock_kb:
        mock_solve.return_value = "x > 2"
        mock_kb.return_value = MagicMock()
        mock_kb.return_value.as_markup.return_value = "keyboard"

        await handle_inequality(message, user_language, texts, history_service)

        mock_solve.assert_called_once_with("x>2")
        message.answer.assert_called_once()
        history_service.save_message.assert_called_once_with(123, "x>2", "x > 2")
