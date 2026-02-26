import logging
from db.engine import engine
from sqlalchemy import text

logger = logging.getLogger(__name__)


# ЗАПУСКАЮТСЯ ПРИ ВЫЗОВЕ
# 1. Для записи пользователя в БД при начале диалога с ботом
async def init_user(user_id: int) -> bool:
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
            await conn.execute(text("INSERT INTO users(user_id, role) VALUES (:user_id, :role)"),
                               {'user_id': user_id, 'role': 'normal'})
            return True
    except Exception:
        logger.error("Ошибка при инициализации пользователя")
        return False


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


# Проверяем роль пользователя и время окончания его подписки при наличии
async def check_user_from_db(user_id):
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("""
            WITH updated as (UPDATE users SET premium_until = NULL, role = 'normal' WHERE user_id = :user_id 
            AND NOW() > premium_until AND role != 'admin' RETURNING premium_until, role)
            SELECT premium_until, role FROM updated
            UNION ALL
            SELECT premium_until, role FROM users
            WHERE user_id = :user_id AND NOT EXISTS (SELECT 1 FROM updated);
            """), {'user_id': user_id})
            user_status = result.fetchone()
            if user_status:
                return str(user_status[0]), user_status[1]
            else:
                logger.error(f"Ошибка проверки статуса, пользователь не найден, user_id: {user_id}")
                return False
    except Exception:
        logger.exception("Ошибка обновления статуса пользователя")
        return False


# Для проверки и ресета количества оставшихся попыток
async def check_and_reset_attempt_left(user_id):
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("""
            WITH updated AS(
            UPDATE users
            SET free_attempts_left = 5, free_attempts_reset = NULL
            WHERE user_id = :user_id AND free_attempts_left <=0 AND free_attempts_reset <= NOW()
            RETURNING free_attempts_left)
            SELECT free_attempts_left FROM updated
            UNION ALL
            SELECT free_attempts_left FROM users
            WHERE user_id = :user_id AND NOT EXISTS (SELECT 1 FROM updated)
            """), {'user_id': user_id})
            return result.fetchone()[0] > 0
    except Exception:
        logger.exception(f'Ошибка при проверке оставшихся попыток, user_id: {user_id}')
        return False


# Функция для уменьшения количества оставшихся попыток и установки времени ресета
async def reduce_attempts_from_db(
        user_id):  # надо проверять, что если =1, тогда делаем 0 и ресет тайм через 24ч, если больше то просто -1
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("""
            UPDATE users
            SET free_attempts_left = free_attempts_left -1,
            free_attempts_reset = CASE WHEN (free_attempts_left-1) <= 0 THEN NOW() + INTERVAL '24 hours'
                                       ELSE free_attempts_reset
            END
            WHERE user_id = :user_id RETURNING free_attempts_left
            """), {'user_id': user_id})
            return result.fetchone()[0]
    except Exception:
        logger.exception(f'Ошибка при измении количества бесплатных использований, user_id: {user_id}')
        return 1  # Возвращаем 1 если ошибка на нашей стороны, чтобы пользователь мог использовать другую функцию и полсе ее выполнения еще раз будет обработка в этой функции


# Функция для банов пользователей
async def ban_user(user_id, admin_id, reason):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
            WITH updated as(
                UPDATE users SET role_before_ban = role, role = 'banned' WHERE user_id = :user_id RETURNING user_id)
            INSERT INTO banned_users (user_id, banned_by, banned_at, reason)
            SELECT :user_id, :banned_by, NOW(), :reason
            FROM updated
            RETURNING user_id
            """), {'user_id': user_id, 'reason': reason, 'banned_by': admin_id})
            return True
    except Exception:
        logger.exception(f"Ошибка при попытке забанить пользователя")
        return False


# Функция для выдачи админки
async def add_admin(admin_id):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
            WITH updated as(
                UPDATE users SET role = 'admin' WHERE user_id = :admin_id RETURNING user_id)
            INSERT INTO admins (admin_id)
            SELECT :admin_id
            FROM updated
            """), {'admin_id': admin_id})
            return True
    except Exception:
        logger.exception(f"Ошибка при попытке забанить пользователя")
        return False


# Функция для выдачи админки
async def remove_admin(admin_id):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
            WITH updated as(
                UPDATE users SET role = CASE
                 WHEN premium_until > NOW() THEN 'premium'
                 WHEN premium_until <= NOW() THEN 'normal' END
                WHERE user_id = :admin_id RETURNING user_id)
            DELETE FROM admins
             WHERE admin_id = :admin_id
             AND EXISTS (SELECT 1 FROM updated)
            """), {'admin_id': admin_id})
            return True
    except Exception:
        logger.exception(f"Ошибка при попытке забанить пользователя")
        return False


# Функция для разбана пользователей
async def unban_user(user_id):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""WITH unbanned as(
            UPDATE users SET role = role_before_ban, role_before_ban = NULL WHERE user_id = :user_id RETURNING user_id)
            UPDATE banned_users SET active = FALSE WHERE user_id IN (SELECT user_id FROM unbanned)"""),
                               {'user_id': user_id})
            return True
    except Exception:
        logger.exception(f"Ошибка при попытке разблокировать пользователя")
        return False
