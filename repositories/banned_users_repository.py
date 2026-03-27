import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

logger = logging.getLogger(__name__)


class BannedRepository:
    def __init__(self, engine):
        self.engine = engine

    async def fetch_bans(self, current_position: int = 0):
        """
        Получает список активных банов с пагинацией.
        """
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("""
                    SELECT id, user_id, banned_by, banned_at, reason FROM banned_users WHERE id > :current_position AND active = True ORDER BY id LIMIT 4
                    """), {"current_position": current_position})
                rows = result.mappings().fetchall()
                return rows
        except SQLAlchemyError:
            logger.exception(f"Ошибка при получении списка банов")
            raise

    async def ban_user(self, user_id, admin_id, reason):
        """
        Блокирует пользователя и сохраняет его предыдущую роль.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.execute(
                    text("UPDATE users SET role_before_ban = role, role = 'banned' WHERE user_id = :user_id"),
                    {'user_id': user_id}
                )

                await conn.execute(
                    text(
                        "INSERT INTO banned_users (user_id, banned_by, banned_at, reason) VALUES (:user_id, :banned_by, NOW(), :reason)"),
                    {'user_id': user_id, 'banned_by': admin_id, 'reason': reason}
                )
        except SQLAlchemyError:
            logger.exception(f"Ошибка при блокировке пользователя")
            raise

    async def unban_user(self, user_id):
        """
        Разблокирует пользователя и восстанавливает его предыдущую роль.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("""
                UPDATE users SET role = role_before_ban, role_before_ban = NULL WHERE user_id = :user_id RETURNING user_id"""),
                                   {'user_id': user_id})

                await conn.execute(text("""UPDATE banned_users SET active = FALSE WHERE user_id = :user_id"""),
                                   {'user_id': user_id})
        except SQLAlchemyError:
            logger.exception(f"Ошибка при разблокировке пользователя")
            raise