from aiogram.filters import BaseFilter
from aiogram import types
from bot.services.AccessService import AccessService
import logging

logger = logging.getLogger(name=__name__)

# NOTE:
# freemium checks use fail-open strategy for UX
# premium/admin checks must always fail-closed
class HasAttemptsLeft(BaseFilter):
    async def __call__(self, message: types.Message, access_service: AccessService, **kwargs):
        role = await access_service.get_user_role(message.from_user.id)
        try:
            if role is None:
                logger.exception(f"Ошибка проверки роли пользователя, user_id:{message.from_user.id}")
                return False
            else:
                if role == 'normal':
                    return await access_service.has_attempts_left(message.from_user.id)
                elif role == 'banned':
                    return False
                else: return True
        except Exception:
            logger.exception("Ошибка проверки доступа пользователя к freemium функции")
            return False
