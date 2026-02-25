from aiogram.filters import BaseFilter
from aiogram import types
from services.AccessRights import AccessRights
import logging

logger = logging.getLogger(name=__name__)

# NOTE:
# freemium checks use fail-open strategy for UX
# premium/admin checks must always fail-closed
class HasAttemptsLeft(BaseFilter):
    async def __call__(self, message: types.Message, access_rights: AccessRights, **kwargs):
        role = await access_rights.check_user(message.from_user.id)
        try:
            if role is None:
                logger.exception(f"Ошибка проверки роли пользователя, user_id:{message.from_user.id}")
                return False
            else:
                if role == 'normal':
                    return await access_rights.attempts_left(message.from_user.id)
                elif role == 'banned':
                    return False
                else: return True
        except Exception:
            logger.exception("Ошибка проверки доступа пользователя к freemium функции")
            return False
