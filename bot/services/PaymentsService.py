# all functions from paymnets
from sqlalchemy.exc import SQLAlchemyError

from bot.core.ServiceResult import ServiceResult
from bot.repositories.stars_transactions_repository import PaymentsRepository


class PaymentsService:
    def __init__(self, repo: PaymentsRepository):
        self.repo = repo

    async def update_subscription_period(self, user_id: int, payload: str, amount: int, charge_id: str) -> ServiceResult:
        """
        Обновляет период подписки пользователя после успешной оплаты.
        """
        try:
            days_part = 0
            product_type = ''
            payload_split = payload.split('_')
            # Проверяем, что начало payload корректно
            if payload.startswith('premium', ):
                days_part = int(payload_split[1]) if len(payload_split) > 1 else None

            if days_part in [30, 90, 365]:  # проверяем что корректно указано количество дней в payload
                product_type = f'premium_{days_part}'
            result_start_transactions_table, result_users_table = await self.repo.insert_into_stars_transactions(
                user_id, payload, amount, charge_id, product_type, days_part)

            if result_start_transactions_table and result_users_table:
                return ServiceResult(success=True, message_key='payments_successful_answer')
            else:
                return ServiceResult(success=False, message_key='payments_failed_answer')
        except SQLAlchemyError:
            return ServiceResult(success=False, message_key='payments_failed_answer')