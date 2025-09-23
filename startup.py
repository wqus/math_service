import asyncio
from aiogram import Dispatcher as Dp
import redis.asyncio as redis
import aiofiles
import aiosqlite
import json
from aiogram.fsm.storage.redis import RedisStorage

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, max_connections=25,
                                 health_check_interval=30, socket_timeout=4)
storage = RedisStorage(redis_client)

async def init_redis(dispatcher: Dp): #устанавливает соединение с редис
    if not await redis_client.ping():
        print("redis error")
    else:
        dispatcher["redis"] = redis_client

async def close_redis(dispatcher: Dp):  # on_shutdown, закрывает соединение с редис
    if redis_client:
        redis_cl: redis.Redis = dispatcher["redis"]
        await redis_cl.close()
        await redis_cl.connection_pool.disconnect()

#1. Загрузка текстовых ресурсов
async def load_texts():
    try:
        async with aiofiles.open('D:\\Python_project\\Math_Bot\\text_ru.json', 'r', encoding='utf-8') as f:
            ru_content = await f.read()
            texts_ru = json.loads(ru_content)
        async with aiofiles.open('D:\\Python_project\\Math_Bot\\text_en.json', 'r', encoding='utf-8') as f:
            en_content = await f.read()
            texts_en = json.loads(en_content)
        return {'language:RU': texts_ru, 'language:EN': texts_en}
    except FileNotFoundError as e:
        print(f"Ошибка загрузки файлов переводов: {e}")
        exit(1)
texts = asyncio.run(load_texts())

#2. Иницилизация ДБ
async def init_bot_db():
    async with aiosqlite.connect('bot_data.db') as conn:
        # Создаем таблицу пользователей
        await conn.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER,
                     language TEXT DEFAULT 'RU',
                     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                     user_states INTEGER DEFAULT 0)''')
        await conn.commit()

async def init_history_db():
    async with aiosqlite.connect('users_history.db') as conn:
        # Создаем таблицу пользователей
        await conn.execute('''CREATE TABLE IF NOT EXISTS history (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER NOT NULL,
                     input_message TEXT NOT NULL,
                     output_message TEXT NOT NULL,
                     created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        await conn.commit()
