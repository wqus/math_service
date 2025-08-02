import aiogram
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from typing import Callable, Any, Dict, Awaitable
import aiosqlite

class Inject_language(BaseMiddleware):
    """
    Получаем данные о языке интерфейса пользователя.
    В коде можем воспользоваться с помощью .user_lanuage
    """
    def __init__(self, db_path):
        self.db_path = db_path
    async def _get_user_language(self, user_id: int) -> str:  # take language value
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.cursor()
            await cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
            result = await cursor.fetchone()
            return result[0] if result else "RU"  # возвращаем язык
    async def __call__(self, handler, event, data):
        try:
            if hasattr(event, 'from_user'):
                data['user_language'] = await self._get_user_language(event.from_user.id)
        except Exception as e:
            print(f"Language error: {e}")
            data['user_language'] = 'RU'
        return await handler(event, data)

