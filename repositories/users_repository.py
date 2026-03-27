import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, engine):
        self.engine = engine

    async def create_user_if_not_exists(self, user_id: int) -> bool:
        """
        Создаёт пользователя при первом запуске.

        Возвращает:
        - True → пользователь создан
        - False → уже существует
        """
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("""
                    SELECT 1 FROM users
                    WHERE user_id = :user_id
                """), {"user_id": user_id})

                if result.first():
                    return False

                await conn.execute(text("""
                    INSERT INTO users(user_id, role)
                    VALUES (:user_id, :role)
                """), {
                    "user_id": user_id,
                    "role": "normal"
                })

                return True

        except SQLAlchemyError:
            logger.error("Ошибка при создании пользователя")
            raise

    async def update_user_language(
            self,
            user_id: int,
            language: str
    ) -> bool:
        """
        Обновляет язык пользователя.

        Возвращает:
        - True → успешно обновлено
        - False → пользователь не найден
        """
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("""
                    UPDATE users
                    SET language = :language
                    WHERE user_id = :user_id
                """), {
                    "user_id": user_id,
                    "language": language
                })

                return result.rowcount > 0

        except SQLAlchemyError:
            logger.error("Ошибка при обновлении языка пользователя")
            raise

    async def fetch_user_access(
            self,
            user_id: int
    ) -> tuple | None:
        """
        Возвращает (premium_until, role).

        Если premium истёк:
        → сбрасывает его и роль (кроме admin)
        """
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("""
                    WITH updated AS (
                        UPDATE users
                        SET premium_until = NULL,
                            role = 'normal'
                        WHERE user_id = :user_id
                          AND premium_until IS NOT NULL
                          AND NOW() > premium_until
                          AND role != 'admin'
                        RETURNING premium_until, role
                    )
                    SELECT premium_until, role FROM updated
                    UNION ALL
                    SELECT premium_until, role FROM users
                    WHERE user_id = :user_id
                      AND NOT EXISTS (SELECT 1 FROM updated)
                """), {"user_id": user_id})

                row = result.fetchone()

                if row:
                    return row[0], row[1]

                return None

        except SQLAlchemyError:
            logger.error("Ошибка при получении access данных пользователя")
            raise

    async def check_and_reset_attempts(
            self,
            user_id: int
    ) -> bool:
        """
        Проверяет наличие попыток.

        Если попытки закончились и время сброса прошло:
        → сбрасывает их на 5

        Возвращает:
        - True → попытки есть
        - False → нет
        """
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("""
                    WITH updated AS (
                        UPDATE users
                        SET free_attempts_left = 5,
                            free_attempts_reset = NULL
                        WHERE user_id = :user_id
                          AND free_attempts_left <= 0
                          AND free_attempts_reset <= NOW()
                        RETURNING free_attempts_left
                    )
                    SELECT free_attempts_left FROM updated
                    UNION ALL
                    SELECT free_attempts_left FROM users
                    WHERE user_id = :user_id
                      AND NOT EXISTS (SELECT 1 FROM updated)
                """), {"user_id": user_id})

                row = result.fetchone()

                return bool(row and row[0] > 0)

        except SQLAlchemyError:
            logger.error("Ошибка при проверке попыток пользователя")
            raise

    async def decrease_attempts(
            self,
            user_id: int
    ) -> int:
        """
        Уменьшает количество попыток на 1.

        Если попытки заканчиваются:
        → устанавливает reset через 24 часа

        Возвращает текущее значение попыток
        """
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("""
                    UPDATE users
                    SET free_attempts_left = free_attempts_left - 1,
                        free_attempts_reset = CASE
                            WHEN (free_attempts_left - 1) <= 0
                            THEN NOW() + INTERVAL '24 hours'
                            ELSE free_attempts_reset
                        END
                    WHERE user_id = :user_id
                    RETURNING free_attempts_left
                """), {"user_id": user_id})

                row = result.fetchone()

                return row[0] if row else 0

        except SQLAlchemyError:
            logger.error("Ошибка при уменьшении попыток пользователя")
            raise
