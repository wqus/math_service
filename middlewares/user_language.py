from aiogram import BaseMiddleware
from sqlalchemy import text
from db.engine import engine

class InjectLanguage(BaseMiddleware):
    """
    Получаем данные о языке интерфейса пользователя.
    В коде можем воспользоваться с помощью .user_language
    """
    async def _get_user_language(self, user_id: int) -> str:  # take language value
        async with engine.connect() as conn:
            result =  await conn.execute(text('SELECT language FROM users WHERE user_id = :user_id'), {'user_id': user_id})
            lang = result.first()
            return lang[0] if lang else "RU"  # возвращаем язык
    async def __call__(self, handler, event, data):
        try:
            if hasattr(event, 'from_user'):
                data['user_language'] = await self._get_user_language(event.from_user.id)
        except Exception as e:
            print(f"Language error: {e}")
            data['user_language'] = 'language:RU'
        return await handler(event, data)
