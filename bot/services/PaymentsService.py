import logging

from sqlalchemy.exc import SQLAlchemyError

from bot.core.ServiceResult import ServiceResult
from bot.repositories.stars_transactions_repository import PaymentsRepository

logger = logging.getLogger(__name__)

class PaymentsService:
    def __init__(self, payments_repo: PaymentsRepository):
        self.payments_repo = payments_repo

    async def update_subscription_period(self, user_id: int, payload: str, amount: int, charge_id: str) -> ServiceResult:
        """
        Обновляет период подписки пользователя после успешной оплаты.
        """
        try:
            payload_split = payload.split('_')
            if not payload.startswith('premium') or len(payload_split) < 2:
                logger.error(f"Некорректный payload формат: {payload}, user_id: {user_id}")
                return ServiceResult(success=False, message_key='payments_failed_answer')
            try:
                days_part = int(payload_split[1])
            except ValueError:
                logger.error(f"Некорректные дни в payload: {payload_split[1]}, user_id: {user_id}")
                return ServiceResult(success=False, message_key='payments_failed_answer')
            if days_part not in [30, 90, 365]:
                logger.error(f"Некорректные значения дней: {days_part}, user_id: {user_id}")
                return ServiceResult(success=False, message_key='payments_failed_answer')
            product_type = f'premium_{days_part}'

            transaction_id, user_id_updated = await self.payments_repo.insert_into_stars_transactions(
                user_id, payload, amount, charge_id, product_type, days_part)

            if transaction_id and user_id_updated:
                return ServiceResult(success=True, message_key='payments_successful_answer')
            else:
                return ServiceResult(success=False, message_key='payments_failed_answer')
        except SQLAlchemyError:
            return ServiceResult(success=False, message_key='payments_failed_answer')