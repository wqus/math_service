import logging

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def get_access_data(self, user_id: int) -> dict:
        """
        Получает кеш прав доступа пользователя (role + premium_until).
        """
        try:
            return await self.redis.hgetall(f"access:{user_id}")
        except Exception:
            logger.exception(f"Ошибка при получении access кеша user={user_id}")
            return {}

    async def set_access_data(self, user_id: int, role: str, premium_until, ttl: int = 600):
        """
        Сохраняет кеш прав доступа пользователя.
        """
        try:
            key = f"access:{user_id}"

            await self.redis.hset(
                key,
                mapping={
                    "role": role,
                    "premium_until": premium_until
                }
            )

            await self.redis.expire(key, ttl)

        except Exception:
            logger.exception(f"Ошибка при записи access кеша user={user_id}")

    async def invalidate_access(self, user_id: int):
        """
        Удаляет кеш прав доступа пользователя.
        """
        try:
            await self.redis.delete(f"access:{user_id}")
        except Exception:
            logger.exception(f"Ошибка при удалении access кеша user={user_id}")

    async def get_attempts(self, user_id: int):
        """
        Получает количество оставшихся попыток.
        """
        try:
            return await self.redis.get(f"attempts:{user_id}")
        except Exception:
            logger.exception(f"Ошибка при получении attempts user={user_id}")
            return None

    async def set_attempts(self, user_id: int, attempts: int, ttl: int = 600):
        """
        Сохраняет количество попыток в кеш.
        """
        try:
            await self.redis.set(f"attempts:{user_id}", attempts, ex=ttl)
        except Exception:
            logger.exception(f"Ошибка при записи attempts user={user_id}")
