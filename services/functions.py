import aiosqlite

#________ЗАПУСКАЮТСЯ ПРИ ВЫЗОВЕ________
#1. Для записи пользователя в БД при начале диалога с ботом
async def init_user(user_id: int) -> bool:
    """
    Добавляем нового пользователя в БД при первом запуске.
    Возвращает True, если пользователь создан, False если уже существует.
    """
    async with aiosqlite.connect('bot_data.db') as conn:
        cursor = await conn.cursor()
        # Проверяем, есть ли пользователь
        await cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        if await cursor.fetchone():
            return False  # Пользователь уже есть

        # Создаём нового
        await cursor.execute('''
        INSERT INTO users (user_id)
        VALUES (?)
        ''', (user_id,))
        await conn.commit()
        cursor.close()
        return True

#1. Для обновления значения языка интерфейса пользователя
async def update_user_language(user_id: int, language: str) -> bool:
    """
    Обновляет язык пользователя.
    Возвращает True при успехе, False если пользователя нет или возникновении ошибки
    """
    try:
        async with aiosqlite.connect('bot_data.db') as conn:
            cursor = await conn.cursor()
            await cursor.execute('''
            UPDATE users 
            SET language = ? 
            WHERE user_id = ?
            ''', (language, str(user_id)))
            await conn.commit() #сохраняем изменения
            return cursor.rowcount > 0  # Были ли обновлены строки? da/net
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        return False