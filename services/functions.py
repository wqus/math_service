from sqlalchemy import text
from startup import engine

#ЗАПУСКАЮТСЯ ПРИ ВЫЗОВЕ
#1. Для записи пользователя в БД при начале диалога с ботом
async def init_user(user_id: int, username) -> bool:
    """
    Добавляем нового пользователя в БД при первом запуске.
    Возвращает True, если пользователь создан, False если уже существует.
    """
    async with engine.begin() as conn:
        # Проверяем, есть ли пользователь
        result = await conn.execute(text('SELECT 1 FROM users WHERE user_id = :user_id'), {'user_id': user_id})
        row = result.first()
        if row:
            return False # Пользователь уже есть
        # Создаём нового
        await conn.execute(text("INSERT INTO users(user_id, username) VALUES (:user_id, :username)"),{'user_id': user_id, 'username': username})
        return True

#1. Для обновления значения языка интерфейса пользователя
async def update_user_language(user_id: int, language: str) -> bool:
    """
    Обновляет язык пользователя.
    Возвращает True при успехе, False если пользователя нет или возникновении ошибки
    """
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text('''
            UPDATE users 
            SET language = :language
            WHERE user_id = :user_id
            '''), {'language': language, 'user_id': user_id})
            return result.rowcount > 0  # Были ли обновлены строки? da/net
    except Exception as e:
        print(f"Error: {e}")
        return False