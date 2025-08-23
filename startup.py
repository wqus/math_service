import asyncio

import redis.asyncio as redis
import aiofiles
import aiosqlite
import json


def init_redis(redis_client):
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, max_connections=25,
                          health_check_interval=30, socket_timeout=4)
    return redis_client
    # redis_c.ping()
    # await init_db()
    # matplotlib.use('Agg')

async def close_redis(redis_client):  # on_shutdown
    if redis_client:
        await redis_client.close()
        redis_client = None

#1. Загрузка текстовых ресурсов
async def load_texts():
    try:
        async with aiofiles.open('text_ru.json', 'r', encoding='utf-8') as f:
            ru_content = await f.read()
            texts_ru = json.loads(ru_content)
        async with aiofiles.open('text_en.json', 'r', encoding='utf-8') as f:
            en_content = await f.read()
            texts_en = json.loads(en_content)
        return {'RU': texts_ru, 'EN': texts_en}
    except FileNotFoundError as e:
        print(f"Ошибка загрузки файлов переводов: {e}")
        exit(1)
texts = asyncio.run(load_texts())

#2. Иницилизация ДБ
async def init_db():
    async with aiosqlite.connect('bot_data.db') as conn:
        # Создаем таблицу пользователей
        await conn.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER,
                     language TEXT DEFAULT 'RU',
                     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                     user_states INTEGER DEFAULT 0)''')
        await conn.commit()

