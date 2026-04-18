import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from bot.presenters.admin_presenter import format_tickets_list


@pytest.mark.asyncio
@patch("bot.presenters.admin_presenter.answer_to_ticket_kb", new_callable=AsyncMock)
async def test_format_tickets_list(mock_kb: AsyncMock):
    mock_kb.return_value = 'MOCK_KB'
    tickets = [
        {
            "id": 1,
            "user_id": 123,
            "send_time": datetime(2024, 1, 1, 12, 0),
            "message": "Hello"
        }
    ]

    texts = {
        "EN": {
            "support_answer_bt": "Answer"
        }
    }

    result = await format_tickets_list(tickets, texts, "EN")

    message, kb = result[0]

    assert len(result) == 1
    assert "Ticket_id: 1" in message
    assert "User_id: 123" in message
    assert "2024-01-01 12:00" in message
    assert '"Hello"' in message

    assert kb == "MOCK_KB"

    mock_kb.assert_called_once_with(1,123, "Answer")
