import logging

from aiogram.filters import BaseFilter
from aiogram import types
from bot.services.AccessService import AccessService

logger = logging.getLogger(name=__name__)


class AccessRightsFilter(BaseFilter):
    def __init__(self, min_level):
        self.min_level = min_level

    async def __call__(self, message: types.Message, access_service: AccessService, **kwargs):
        role = await access_service.get_user_role(message.from_user.id)
        if role is None:
            logger.exception(f"Ошибка проверки роли пользователя, user_id:{message.from_user.id}")
            return False
        else:
            if role == 'owner':
                level = 3
            elif role == 'admin':
                level = 2
            elif role == 'premium':
                level = 1
            elif role == 'normal':
                level = 0
            else: level = -1
            return level >= self.min_level
