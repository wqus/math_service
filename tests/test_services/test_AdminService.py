import pytest
from bot.services.AdminService import AdminService
from unittest.mock import AsyncMock
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, timezone


@pytest.mark.asyncio
async def test_create_support_message_success():
    mock_ticket_repo = AsyncMock()
    mock_ticket_repo.create_support_message.return_value = 1

    service = AdminService(
        ticket_repo=mock_ticket_repo,
        ban_repo=AsyncMock()
    )

    result = await service.create_support_message(1,'message')

    assert result.success == True
    assert result.message_key == 'support_message_saved'
    assert result.data == {'ticket_id': 1}

    mock_ticket_repo.create_support_message.assert_called_once_with(1,'message')


@pytest.mark.asyncio
async def test_create_support_message_db_error():
    mock_ticket_repo = AsyncMock()
    mock_ticket_repo.create_support_message.side_effect = SQLAlchemyError()

    service = AdminService(
        ticket_repo=mock_ticket_repo,
        ban_repo=AsyncMock()
    )

    result = await service.create_support_message(1, 'message')

    assert result.success == False
    assert result.message_key == 'support_message_failed'

    mock_ticket_repo.create_support_message.assert_called_once_with(1, 'message')

@pytest.mark.asyncio
async def test_fetch_tickets_success():
    tickets = [
        {'id': 1, 'message': 'test1'},
        {'id': 2, 'message': 'test2'},
        {'id': 3, 'message': 'test3'},
    ]

    mock_ticket_repo = AsyncMock()
    mock_ticket_repo.fetch_open_tickets.return_value = tickets

    service = AdminService(
        ticket_repo=mock_ticket_repo,
        ban_repo=AsyncMock()
    )

    result = await service.fetch_tickets()

    assert result.success == True
    assert result.message_key == 'support_no_tickets_to_load'
    assert result.data['tickets'] == tickets
    assert result.data['has_more'] == False
    assert result.data['last_ticket_id'] == 3
    mock_ticket_repo.fetch_open_tickets.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_fetch_tickets_db_error():
    mock_ticket_repo = AsyncMock()
    mock_ticket_repo.fetch_open_tickets.side_effect = SQLAlchemyError()

    service = AdminService(
        ticket_repo=mock_ticket_repo,
        ban_repo=AsyncMock()
    )

    result = await service.fetch_tickets()

    assert result.success == False
    assert result.message_key == 'fetch_tickets_error'
    assert result.data['tickets'] == []
    assert result.data['has_more'] == False
    assert result.data['last_ticket_id'] is None
    mock_ticket_repo.fetch_open_tickets.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_save_support_answer():
    mock_ticket_repo = AsyncMock()
    mock_ticket_repo.update_ticket_with_answer.return_value = True

    service = AdminService(
        ticket_repo=mock_ticket_repo,
        ban_repo=AsyncMock()
    )

    result = await service.save_support_answer(1, 'answer', 123)

    assert result.success == True
    assert result.message_key == 'support_success_answer'
    mock_ticket_repo.update_ticket_with_answer.assert_called_once_with(1, 'answer', 123)

@pytest.mark.asyncio
async def test_save_support_answer_db_error():
    mock_ticket_repo = AsyncMock()
    mock_ticket_repo.update_ticket_with_answer.side_effect = SQLAlchemyError()

    service = AdminService(
        ticket_repo=mock_ticket_repo,
        ban_repo=AsyncMock()
    )

    result = await service.save_support_answer(1, 'answer', 123)

    assert result.success == False
    assert result.message_key == 'support_failed_answer'
    mock_ticket_repo.update_ticket_with_answer.assert_called_once_with(1, 'answer', 123)


@pytest.mark.asyncio
async def test_fetch_bans_success():
    bans = [
        {'id': 1, 'user_id': 1, 'banned_by': 123,'banned_at': (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(), 'reason': 'reason1'},
        {'id': 2, 'user_id': 2, 'banned_by': 132,'banned_at': (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(), 'reason': 'reason2'},
        {'id': 3, 'user_id': 3, 'banned_by': 213,'banned_at': (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(), 'reason': 'reason3'},
        {'id': 4, 'user_id': 4, 'banned_by': 231, 'banned_at': (datetime.now(timezone.utc)).isoformat(), 'reason': 'reason3'},

    ]

    mock_ban_repo = AsyncMock()
    mock_ban_repo.fetch_bans.return_value = bans

    service = AdminService(
        ticket_repo=AsyncMock(),
        ban_repo=mock_ban_repo
    )

    result = await service.fetch_bans()

    assert result.success == True
    assert result.message_key == 'load_more'
    assert result.data['bans'] == bans
    assert result.data['has_more'] == True
    assert result.data['last_ban_id'] == 4
    mock_ban_repo.fetch_bans.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_fetch_bans_db_error():
    mock_ban_repo = AsyncMock()
    mock_ban_repo.fetch_bans.side_effect = SQLAlchemyError()

    service = AdminService(
        ticket_repo=AsyncMock(),
        ban_repo=mock_ban_repo
    )

    result = await service.fetch_bans()

    assert result.success == False
    assert result.message_key == 'fetch_bans_error'
    assert result.data['bans'] == []
    assert result.data['has_more'] == False
    assert result.data['last_ban_id'] is None
    mock_ban_repo.fetch_bans.assert_called_once_with(1)


