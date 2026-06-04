import pytest
from unittest.mock import AsyncMock, patch

from bot.handlers.payments import show_premium_options


@pytest.mark.asyncio
async def test_show_premium_options():
    message = AsyncMock()
    message.bot = AsyncMock()
    message.answer = AsyncMock()

    texts = {
        "RU": {
            "premium_description_for_link": "Premium подписка",
            "premium": "Премиум",
            "premium_answer": "Выберите подписку",
            "premium_choose": "Варианты:"
        }
    }

    with patch('bot.handlers.payments.create_stars_invoice_link', new=AsyncMock()) as mock_link, \
            patch('bot.handlers.payments.payment_kb', new=AsyncMock()) as mock_kb:
        mock_link.side_effect = ["link1", "link2", "link3"]
        mock_kb.return_value = "keyboard"

        await show_premium_options(message, "RU", texts)

        assert message.answer.call_count == 2
        mock_kb.assert_called_once_with("RU", link1m="link1", link3m="link2", link12m="link3")
