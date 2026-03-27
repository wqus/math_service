import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

logger = logging.getLogger(__name__)


class TicketRepository:
    def __init__(self, engine):
        self.engine = engine

    async def create_support_message(self, user_id: int, message: str) -> int:
        """
        Сохраняет запрос пользователя в поддержку.
        """
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("""
                INSERT INTO support_messages(user_id, message)
                VALUES (:user_id, :message)
                RETURNING id"""), {'user_id': user_id, 'message': message})

                return result.fetchone()[0]
        except SQLAlchemyError:
            logger.exception(f"Ошибка при сохранении обращения, user_id: {user_id}")
            raise

    async def fetch_open_tickets(self, current_position: int = 0) -> dict:
        """
        Получает открытые тикеты с пагинацией.
        """
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("""
                SELECT id, user_id, send_time, message, status FROM support_messages WHERE id > :current_position AND status = 'open' ORDER BY id LIMIT 4 
                """), {"current_position": current_position})

                rows = result.mappings().fetchall()
                return rows
        except SQLAlchemyError:
            logger.exception(f"Ошибка при получении тикетов из БД")
            raise

    async def update_ticket_with_answer(self, ticket_id: int, answer: str, admin_id: int) -> None:
        """
        Сохраняет ответ на тикет и закрывает его.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("""
                UPDATE support_messages SET status = 'closed', answered_at = NOW(), answered_by = :admin_id, answer_message = :answer WHERE id = :id"""),
                                   {'id': ticket_id, 'admin_id': admin_id, 'answer': answer})
        except SQLAlchemyError:
            logger.exception(f"Ошибка при сохранении ответа на тикет")
            raise

    async def save_ticket_rating(self, rating: int, ticket_id: int):
        """
        Сохраняет оценку ответа поддержки от пользователя.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("""
                UPDATE support_messages SET rating = :rating WHERE id = :ticket_id"""),
                                   {'ticket_id': ticket_id, 'rating': int(rating)})
                return True
        except SQLAlchemyError:
            logger.exception(f"Ошибка при сохранении оценки тикета")
            raise