import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

logger = logging.getLogger(__name__)


class AdminRepository:
    def __init__(self, engine):
        self.engine = engine

    async def add_admin(self, admin_id):
        """
        Назначает пользователя администратором.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("""UPDATE users SET role = 'admin' WHERE user_id = :admin_id)
                """), {'admin_id': admin_id})
        except SQLAlchemyError:
            logger.exception(f"Ошибка при назначении администратора")
            raise

    async def remove_admin(self, admin_id):
        """
        Удаляет роль администратора у пользователя.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("""
                    UPDATE users SET role = CASE
                    WHEN premium_until > NOW() THEN 'premium'
                    WHEN premium_until <= NOW() THEN 'normal' END
                    WHERE user_id = :admin_id
                """), {'admin_id': admin_id})
        except SQLAlchemyError:
            logger.exception(f"Ошибка при удалении администратора")
            raise