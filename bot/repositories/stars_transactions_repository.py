import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

logger = logging.getLogger(__name__)

class PaymentsRepository:
    def __init__(self, engine):
        self.engine = engine
    # Вставка информации о платеже в таблицу stars_transactions
    async def insert_into_stars_transactions(self, user_id: int, payload: str, amount: int, charge_id: str, product_type: str,
                                             days: int):
        """
        Обновляет значение периода подписки.
        Возвращает True при успехе, False если возникла ошибка во время обработки платежа
        """
        logger.info(f"Обработка платежа user: {user_id}")
        try:
            async with self.engine.begin() as conn:
                # Запрос для добавления транзакции в таблицу stars_transactions
                result = await conn.execute(text('''INSERT INTO stars_transactions (user_id, payload, amount, 
                            purchased_at, charge_id, status, product_type)
                            VALUES (:user_id, :payload, :amount, NOW(), :charge_id, 'success', :product_type)
                            RETURNING id
                '''), {'user_id': user_id, 'payload': payload, 'amount': amount, 'charge_id': charge_id,
                       'product_type': product_type})
                result_users = await conn.execute(text('''
                            UPDATE USERS
                            SET premium_until = COALESCE(premium_until, NOW()) + :premium_until * INTERVAL '1 day', premium_plan = :premium_plan, last_premium_at = NOW(),
                            free_attempts_left = 0, role = 'premium' WHERE user_id = :user_id;'''),
                                                  {'premium_until': days, 'premium_plan': product_type,
                                                   'user_id': user_id})
                return result.fetchall(), result_users.fetchall()
        except SQLAlchemyError:
            logger.exception(f"Ошибка при занесении/обновлении платежа в бд, user: {user_id}; charge_id: {charge_id}")
            raise
