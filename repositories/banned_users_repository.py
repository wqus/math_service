import logging

from db.engine import engine
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Функция для сохранения оценки ответа поддержки от пользователя
async def take_bans(current_position: int = 0):
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("""
            SELECT id, user_id, banned_by, banned_at, reason FROM support_messages WHERE id > :current_position AND active = True ORDER BY id LIMIT 4 
            """), {"current_position": current_position})

            rows = result.mappings().fetchall()  # чтобы был словарь
            has_more = False  # если True -> отправляем сообщение админу "Загрузить еще?", если False -> "Банов больше нет!"

            if len(rows) >= 4:
                has_more = True
                rows.pop()  # возвращаем только три тикета

            return rows, has_more
    except Exception:
        logger.exception(f"Ошибка при попытке получить из БД тикеты")
        return None