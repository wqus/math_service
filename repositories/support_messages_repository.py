import logging

from telebot.apihelper import remove_user_verification

from db.engine import engine
from sqlalchemy import text

logger = logging.getLogger(__name__)


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


# Функция для сохранения запроса пользователя в бд
async def save_message_to_support(user_id, message):
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("""
            INSERT INTO support_messages(user_id, message)
            VALUES (:user_id, :message)
            RETURNING id"""), {'user_id': user_id, 'message': message})

            return result.fetchone()[0]
    except Exception:
        logger.exception(f"Ошибка при вставке обращений, user_id: {user_id}")
        return None


# Функция для извлечения 3х тикетов
async def take_tickets_for_support(current_position: int = 0):
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("""
            SELECT id, user_id, send_time, message, status FROM support_messages WHERE id > :current_position AND status = 'open' ORDER BY id LIMIT 4 
            """), {"current_position": current_position})

            rows = result.mappings().fetchall()  # чтобы был словарь
            has_more = False  # если True -> отправляем сообщение админу "Загрузить еще?", если False -> "Тикетов больше нет!"

            if len(rows) >= 4:
                has_more = True
                rows.pop()  # возвращаем только три тикета

            return rows, has_more
    except Exception:
        logger.exception(f"Ошибка при попытке получить из БД тикеты")
        return None


# Функция для сохранения в бд ответа на тикет и обновления статуса на "closed"
async def save_support_answer_to_db(ticket_id, answer, admin_id):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
            UPDATE support_messages SET status = 'closed', answered_at = NOW(), answered_by = :admin_id, answer_message = :answer WHERE id = :id"""),
                               {'id': int(ticket_id), 'admin_id': admin_id, 'answer': answer})
    except Exception:
        logger.exception(f"Ошибка при попытке сохранить ответ и обновить статус")


# Функция для сохранения оценки ответа поддержки от пользователя
async def save_support_answer_rating(rating, ticket_id):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("""
            UPDATE support_messages SET rating = :rating WHERE id = :ticket_id"""), {'ticket_id': int(ticket_id), 'rating': int(rating)})
    except Exception:
        logger.exception(f"Ошибка при попытке сохранить оценку пользователя на сообщение поддержки")

