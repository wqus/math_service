import logging

from aiogram.filters import BaseFilter
from aiogram import types
from services.AccessRights import AccessRights

logger = logging.getLogger(name=__name__)


class AccessRightsFilter(BaseFilter):
    def __init__(self, min_level):
        self.min_level = min_level

    async def __call__(self, message: types.Message, access_rights: AccessRights, **kwargs):
        role = await access_rights.check_user(message.from_user.id)
        if role is None:
            logger.exception(f"Ошибка проверки роли пользователя, user_id:{message.from_user.id}")
            return False
        else:
            if role == 'admin':
                level = 2
            elif role == 'premium':
                level = 1
            else:
                level = 0
            return level >= self.min_level
