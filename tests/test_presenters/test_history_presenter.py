import pytest

from bot.presenters.history_presenter import format_history_list
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_format_history_list():
    mock_kb = AsyncMock()
    rows = [
        {
            "input_message": "2 + 2",
            "output_message": "4"
        },
        {
            "input_message": "sin(π/2) * 10",
            "output_message": "10"
        },
        {
            "input_message": "∫x² dx от 0 до 1",
            "output_message": "1/3"
        },
        {
            "input_message": "solve x² - 5x + 6 = 0",
            "output_message": "x = 2, x = 3"
        }
    ]
    texts = {
        "language: RU": {
            "answer": "Ответ:",
            "no_history_saves": "У вас пока нет сохранённой истории."
        }
    }
    language = 'language: RU'
    with patch("bot.presenters.history_presenter.page_keyboard", return_value = mock_kb) as mock_page_kb:
        history_text, pagination_kb = await format_history_list(rows, None, None, texts, language)

        mock_page_kb.assert_called_once_with(None, None)
        assert pagination_kb == mock_kb

        expected_parts = [
            "• 2 + 2;\tОтвет: <b>4</b>",
            "• sin(π/2) * 10;\tОтвет: <b>10</b>",
            "• ∫x² dx от 0 до 1;\tОтвет: <b>1/3</b>",
            "• solve x² - 5x + 6 = 0;\tОтвет: <b>x = 2, x = 3</b>"
        ]

        for part in expected_parts:
            assert part in history_text



