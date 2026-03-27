import datetime
import logging

import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

logger = logging.getLogger(__name__)


class HistoryRepository:
    def __init__(self, engine):
        self.engine = engine

    async def fetch_user_history(
            self,
            user_id: int,
            cursor: tuple | None = None,
            limit: int = 10,
            direction: str = "next"
    ) -> list:
        """
        Получает историю сообщений пользователя с курсорной пагинацией.
        """
        try:
            query = """
                SELECT id, input_message, output_message, created_at
                FROM history
                WHERE user_id = :user_id
            """
            params = {"user_id": user_id, "limit": limit}

            if cursor:
                cursor_id, cursor_created_at = cursor
                params["created_at"] = cursor_created_at
                params["id"] = cursor_id

                if direction == "next":
                    query += """
                        AND (created_at < :created_at
                        OR (created_at = :created_at AND id < :id))
                    """
                else:
                    query += """
                        AND (created_at > :created_at
                        OR (created_at = :created_at AND id > :id))
                    """

            if direction == "prev":
                query += " ORDER BY created_at ASC, id ASC LIMIT :limit"
            else:
                query += " ORDER BY created_at DESC, id DESC LIMIT :limit"

            async with self.engine.connect() as conn:
                result = await conn.execute(text(query), params)
                return result.mappings().fetchall()

        except SQLAlchemyError:
            logger.error("Ошибка при получении истории пользователя")
            raise

    async def has_newer_records(
            self,
            user_id: int,
            created_at: datetime.datetime,
            record_id: int
    ) -> bool:
        """
        Проверяет, есть ли более новые записи.
        """
        async with self.engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT 1 FROM history
                WHERE user_id = :user_id
                AND (created_at > :created_at
                     OR (created_at = :created_at AND id > :id))
                LIMIT 1
            """), {
                "user_id": user_id,
                "created_at": created_at,
                "id": record_id
            })

            return bool(result.first())

    async def has_older_records(
            self,
            user_id: int,
            created_at: datetime.datetime,
            record_id: int
    ) -> bool:
        """
        Проверяет, есть ли более старые записи.
        """
        async with self.engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT 1 FROM history
                WHERE user_id = :user_id
                AND (created_at < :created_at
                     OR (created_at = :created_at AND id < :id))
                LIMIT 1
            """), {
                "user_id": user_id,
                "created_at": created_at,
                "id": record_id
            })

            return bool(result.first())

    async def create_message_record(
            self,
            user_id: int,
            input_text: str,
            output_text: str
    ) -> None:
        """
        Сохраняет сообщение пользователя в истории.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("""
                    INSERT INTO history(user_id, input_message, output_message)
                    VALUES (:user_id, :input_text, :output_text)
                """), {
                    "user_id": user_id,
                    "input_text": input_text,
                    "output_text": output_text
                })

        except SQLAlchemyError:
            logger.error("Ошибка при сохранении сообщения")
            raise
