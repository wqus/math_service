from sqlalchemy import text
from db.engine import engine
import logging

logger = logging.getLogger(name=__name__)


# ЗАПУСКАЮТСЯ ПРИ ВЫЗОВЕ
# 1. Для записи пользователя в БД при начале диалога с ботом
async def init_user(user_id: int, username) -> bool:
    """
    Добавляем нового пользователя в БД при первом запуске.
    Возвращает True, если пользователь создан, False если уже существует.
    """
    try:
        logger.info("Инициализация пользователя")
        async with engine.begin() as conn:
            # Проверяем, есть ли пользователь
            result = await conn.execute(text('SELECT 1 FROM users WHERE user_id = :user_id'), {'user_id': user_id})
            row = result.first()
            if row:
                return False  # Пользователь уже есть
            # Создаём нового
            await conn.execute(text("INSERT INTO users(user_id, username) VALUES (:user_id, :username)"),
                               {'user_id': user_id, 'username': username})
            return True
    except Exception:
        logger.error("Ошибка при инициализации пользователя")


# 1. Для обновления значения языка интерфейса пользователя
async def update_user_language(user_id: int, language: str) -> bool:
    """
    Обновляет язык пользователя.
    Возвращает True при успехе, False если пользователя нет или возникновении ошибки
    """
    logger.debug("Обновления языка пользователя")
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text('''
            UPDATE users 
            SET language = :language
            WHERE user_id = :user_id
            '''), {'language': language, 'user_id': user_id})
            return result.rowcount > 0  # Были ли обновлены строки? da/net
    except Exception as e:
        logger.error("Ошибка обновления языка пользователя")
        return False


# Обработка платежа покупки премиум
async def update_subscription_period(user_id: int, payload: str, amount: int, charge_id: str):
    """
    Обновляет значение периода подписки.
    Возвращает True при успехе, False если возникла ошибка во время обработки платежа
    """
    logger.info(f"Обработка платежа user: {user_id}")
    try:
        async with engine.begin() as conn:
            payload_split = payload.split('_')

            # Проверяем, что начало payload корректно
            if payload.startswith('premium:', ):
                days_part = int(payload_split[1]) if len(payload_split) > 1 else None
            else:
                logger.warning(
                    f"Ошибка при обработке payload платежа, payload начинатся не с premium:. User: {user_id}; charge_id: {charge_id}")
                return False
            if days_part in [30, 90, 365]:  # проверяем что корректно указано количество дней в payload
                product_type = f'premium_{days_part}'
            else:
                logger.warning(
                    f'Ошибка при обработке обработке платежа. Некорректный days_part. User: {user_id}; charge_id: {charge_id}')
                return False

            # Запрос для добавления транзакции в таблицу stars_transactions
            result_star = await conn.execute(text('''INSERT INTO stars_transactions (user_id, payload, amount, 
            purchased_at, charge_id, status, product_type)
            VALUES (:user_id, :payload, :amount, NOW(), :charge_id, 'success', :product_type) ON CONFLICT (charge_id) DO NOTHING
            RETURNING id
            '''), {'user_id': user_id, 'payload': payload, 'amount': amount, 'charge_id': charge_id,
                   'product_type': product_type})

            # Если вставка прошла успешно -> обновляем параметры пользователя в таблице users
            if result_star.rowcount > 0:
                result_users = await conn.execute(text('''
                UPDATE USERS
                SET premium_until = COALESCE(premium_until, NOW()) + :premium_until * INTERVAL '1 day', premium_plan = :premium_plan, last_premium_at = NOW(),
                free_attempts_left = 0, role = 'premium' WHERE user_id = :user_id;'''),
                                                  {'premium_until': days_part, 'premium_plan': product_type,
                                                   'user_id': user_id})

                # При неудачном обновлении значений, например не найден пользователь останавливаем работу
                if result_users.rowcount == 0:
                    logger.exception(
                        f"Ошибка при обработке платежа. Неудачный update users. User: {user_id};charge_id: {charge_id}")
                    return False

            # Если вставка транзакции неудачная (result_star == 0), например транзакции строка с таким charge_id уже существует
            else:
                logger.warning(
                    f"Ошибка при обработке платежа. Транзакция с charge_id = {charge_id} уже существует. User: {user_id}")
                return False

            # Возвращаем успешный результат обработки платежа
            logger.info(f"Успешная обработка платежа. Транзакция {result_star.fetchone()[0]} User: {user_id}")
            return True
    except Exception:
        logger.exception(f"Ошибка при обработке платежа user: {user_id}; charge_id: {charge_id}")
        return False
