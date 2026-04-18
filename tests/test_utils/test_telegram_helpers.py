import pytest
from bot.utils.telegram_helpers import send_tickets
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_send_tickets():
    message = AsyncMock()

    language = "EN"
    texts = {
        "EN": {
            "support_no_tickets_to_load": "No tickets"
        }
    }
    result = AsyncMock()
    result.data = {"tickets": [1, 2, 3, 4]}

    fake_formated = [
        ("msg1", AsyncMock()),
        ("msg2", AsyncMock()),
        ("msg3", AsyncMock()),
        ("msg4", AsyncMock()),
    ]

    with patch("bot.utils.telegram_helpers.format_tickets_list", AsyncMock(return_value=fake_formated)):
        await send_tickets(message, result, language, texts)

    assert message.answer.call_count == 3
