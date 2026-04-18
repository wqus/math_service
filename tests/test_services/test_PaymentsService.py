import pytest
from unittest.mock import AsyncMock
from sqlalchemy.exc import SQLAlchemyError
from bot.services.PaymentsService import PaymentsService


@pytest.mark.asyncio
async def test_update_subscription_period_success():
    mock_payments_repo = AsyncMock()
    mock_payments_repo.insert_into_stars_transactions.return_value = (1, 1)

    payload = 'premium_30_days_1'
    charge_id = 'charge_123456'

    service = PaymentsService(
        payments_repo=mock_payments_repo
    )

    result = await service.update_subscription_period(1, payload, 250, charge_id)

    assert result.success == True
    assert result.message_key == 'payments_successful_answer'
    mock_payments_repo.insert_into_stars_transactions.assert_called_once_with(1, payload, 250, charge_id, 'premium_30',
                                                                              30)


@pytest.mark.asyncio
async def test_update_subscription_invalid_payload():
    payload = 'premium'
    charge_id = 'charge_123456'

    service = PaymentsService(
        payments_repo=AsyncMock()
    )

    result = await service.update_subscription_period(1, payload, 250, charge_id)

    assert result.success == False
    assert result.message_key == 'payments_failed_answer'


@pytest.mark.asyncio
async def test_update_subscription_invalid_days():
    payload = 'premium_30days_1'
    charge_id = 'charge_123456'

    service = PaymentsService(
        payments_repo=AsyncMock()
    )

    result = await service.update_subscription_period(1, payload, 250, charge_id)

    assert result.success == False
    assert result.message_key == 'payments_failed_answer'


@pytest.mark.asyncio
async def test_update_subscription_invalid_days_value():
    payload = 'premium_60_days_1'
    charge_id = 'charge_123456'

    service = PaymentsService(
        payments_repo=AsyncMock()
    )

    result = await service.update_subscription_period(1, payload, 250, charge_id)

    assert result.success == False
    assert result.message_key == 'payments_failed_answer'


@pytest.mark.asyncio
async def test_update_subscription_no_transaction_id():
    mock_payments_repo = AsyncMock()
    mock_payments_repo.insert_into_stars_transactions.return_value = (None, 1)

    payload = 'premium_30_days_1'
    charge_id = 'charge_123456'

    service = PaymentsService(
        payments_repo=mock_payments_repo
    )

    result = await service.update_subscription_period(1, payload, 250, charge_id)

    assert result.success == False
    assert result.message_key == 'payments_failed_answer'
    mock_payments_repo.insert_into_stars_transactions.assert_called_once_with(1, payload, 250, charge_id, 'premium_30',
                                                                              30)


@pytest.mark.asyncio
async def test_update_subscription_period_db_error():
    mock_payments_repo = AsyncMock()
    mock_payments_repo.insert_into_stars_transactions.side_effect = SQLAlchemyError()

    payload = 'premium_30_days_1'
    charge_id = 'charge_123456'

    service = PaymentsService(
        payments_repo=mock_payments_repo
    )

    result = await service.update_subscription_period(1, payload, 250, charge_id)

    assert result.success == False
    assert result.message_key == 'payments_failed_answer'
    mock_payments_repo.insert_into_stars_transactions.assert_called_once_with(1, payload, 250, charge_id, 'premium_30',
                                                                              30)
