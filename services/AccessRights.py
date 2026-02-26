import logging
from datetime import datetime, timezone

import redis.asyncio as redis
from repositories.users_repository import check_user_from_db, reduce_attempts_from_db
import logging
from repositories.users_repository import check_and_reset_attempt_left

logger = logging.getLogger(name=__name__)


class AccessRights:
    def __init__(self, redis_client: redis):
        self.redis_client = redis_client

    # Функция для определения прав доступа пользователя
    async def check_user(self, user_id: int):
        try:
            role_and_premium_until = await self.redis_client.hgetall(f"access:{user_id}")
            until_str = role_and_premium_until.get('premium_until', 'None')
            if until_str != 'None' and datetime.fromisoformat(until_str) > datetime.now(timezone.utc):
                # Если в Redis есть кеш для юзера и premium_until не просрочен то возвращаем значения оттуда
                return role_and_premium_until.get('role')
            # Если такого кеша нет или premium_until просрочен -> обращаемся к БД, берем статус оттуда и записываем в Redis
            else:
                premium_until, role = await check_user_from_db(user_id)
                ttl = 600
                # Устанавливаем значения в хэш
                await self.redis_client.hset(
                    f'access:{user_id}',
                    mapping={'role': role, 'premium_until': premium_until}
                )

                # Устанавливаем TTL отдельной командой
                await self.redis_client.expire(f'access:{user_id}', ttl)
                return role
        except Exception:
            logger.exception(f"Ошибка при проверке прав доступа, user = {user_id}")
            return 'normal' #для положитлеьного UX, чтобы не отказывать в freemium функциях по нашей вине

    # функция для инвалидации кеша
    async def invalidate_cache(self, user_id):
        try:
            await self.redis_client.delete(f'access:{user_id}')
        except Exception:
            logger.exception(f"Ошибка при инвалидации кеша, user: {user_id}")

    # функция для ПРОВЕРКИ того, остались ли попытки использования
    async def attempts_left(self, user_id):
        try:
            attempts = await self.redis_client.get(f"attempts:{user_id}")

            if attempts:
                return int(attempts) > 0
            else:
                return await check_and_reset_attempt_left(user_id)
        except Exception:
            logger.exception(
                f"Ошибка при проверке количества бесплатных использований у пользователя, user_id: {user_id}")
            return True #для положитлеьного UX, чтобы не отказывать в freemium функциях по нашей вине

    # Функция для уменьшения количества попыток в редисе и бд
    async def reduce_number_of_attempts(self, user_id):
        try:
            current_attempts = await reduce_attempts_from_db(
                user_id)  # надо проверять, что если =1, тогда делаем 0 и ресет тайм через 24ч, если больше то просто -1
            await self.redis_client.set(f'attempts:{user_id}', current_attempts, ex=600)
            return current_attempts
        except:
            logger.exception(
                f"Ошибка при уменьшении количества бесплатных использований пользователя, user_id: {user_id}")
            return 1 #если ошибка на нашей стороне, то возвращаем 1

