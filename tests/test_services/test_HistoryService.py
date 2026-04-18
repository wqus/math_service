import pytest
from unittest.mock import AsyncMock
from sqlalchemy.exc import SQLAlchemyError
from bot.services.HistoryService import HistoryService
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
rows = [
    {'id': 1, 'user_id': 123, 'input_message': '2 + 2', 'output_message': '4',
     'created_at': now - timedelta(days=1)},
    {'id': 2, 'user_id': 123, 'input_message': 'x + 5 = 10', 'output_message': 'x = 5',
     'created_at': now - timedelta(days=2)},
    {'id': 3, 'user_id': 123, 'input_message': '15 * 3', 'output_message': '45',
     'created_at': now - timedelta(days=3)},
    {'id': 4, 'user_id': 123, 'input_message': '100 / 4', 'output_message': '25',
     'created_at': now - timedelta(days=4)},
    {'id': 5, 'user_id': 123, 'input_message': 'x^2 = 16', 'output_message': 'x = ±4',
     'created_at': now - timedelta(days=5)},
    {'id': 6, 'user_id': 123, 'input_message': 'sin(30)', 'output_message': '0.5',
     'created_at': now - timedelta(days=6)},
    {'id': 7, 'user_id': 123, 'input_message': '3x + 7 = 22', 'output_message': 'x = 5',
     'created_at': now - timedelta(days=7)},
    {'id': 8, 'user_id': 123, 'input_message': '48 / 6', 'output_message': '8',
     'created_at': now - timedelta(days=8)},
    {'id': 9, 'user_id': 123, 'input_message': '5^3', 'output_message': '125',
     'created_at': now - timedelta(days=9)},
    {'id': 10, 'user_id': 123, 'input_message': 'sqrt(144)', 'output_message': '12',
     'created_at': now - timedelta(days=10)},
]

@pytest.mark.asyncio
async def test_get_user_history_next_direction():
    mock_history_repo = AsyncMock()

    mock_history_repo.fetch_user_history.return_value = rows
    mock_history_repo.has_newer_records.return_value = True
    mock_history_repo.has_older_records.return_value = True

    service = HistoryService(
        history_repo=mock_history_repo,
    )
    result = await service.get_user_history(1, direction='next')

    assert result.success == True
    assert result.message_key == 'history_answer'
    assert result.data['rows'] == rows
    assert result.data['prev_cursor'] == (rows[0]["id"], rows[0]["created_at"])
    assert result.data['next_cursor'] == (rows[-1]["id"], rows[-1]["created_at"])

    mock_history_repo.fetch_user_history.assert_called_once_with(1, None, direction='next')
    mock_history_repo.has_newer_records.assert_called_once_with(1, rows[0]["created_at"], rows[0]["id"])
    mock_history_repo.has_older_records.assert_called_once_with(1, rows[-1]["created_at"], rows[-1]["id"])

@pytest.mark.asyncio
async def test_get_user_history_prev_direction():
    mock_history_repo = AsyncMock()
    expected_rows = rows[::-1]
    mock_history_repo.fetch_user_history.return_value = expected_rows
    mock_history_repo.has_newer_records.return_value = True
    mock_history_repo.has_older_records.return_value = True

    service = HistoryService(
        history_repo=mock_history_repo,
    )
    result = await service.get_user_history(1, direction='prev')

    assert result.success == True
    assert result.message_key == 'history_answer'
    assert result.data['rows'] == expected_rows
    assert result.data['prev_cursor'] == (expected_rows[0]["id"], expected_rows[0]["created_at"])
    assert result.data['next_cursor'] == (expected_rows[-1]["id"], expected_rows[-1]["created_at"])

    mock_history_repo.fetch_user_history.assert_called_once_with(1, None, direction='prev')
    mock_history_repo.has_newer_records.assert_called_once_with(1, expected_rows[0]["created_at"], expected_rows[0]["id"])
    mock_history_repo.has_older_records.assert_called_once_with(1, expected_rows[-1]["created_at"], expected_rows[-1]["id"])

@pytest.mark.asyncio
async def test_get_user_history_db_error():
    mock_history_repo = AsyncMock()

    mock_history_repo.fetch_user_history.side_effect = SQLAlchemyError()
    mock_history_repo.has_newer_records.return_value = True
    mock_history_repo.has_older_records.return_value = True

    service = HistoryService(
        history_repo=mock_history_repo,
    )
    result = await service.get_user_history(1, direction='next')

    assert result.success == False
    assert result.message_key == 'history_error'
    assert result.data['rows'] == []
    assert result.data['prev_cursor'] is None
    assert result.data['next_cursor'] is None

    mock_history_repo.fetch_user_history.assert_called_once_with(1, None, direction='next')
    mock_history_repo.has_newer_records.assert_not_called()
    mock_history_repo.has_older_records.assert_not_called()

