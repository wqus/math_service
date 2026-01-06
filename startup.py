import asyncio
from aiogram import Dispatcher as Dp
import redis.asyncio as redis
import aiofiles
import json
from aiogram.fsm.storage.redis import RedisStorage
from sqlalchemy.ext.asyncio import create_async_engine
import asyncpg

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

database_url = (
    "postgresql+asyncpg://bot:botpass@localhost:5432/bot_db"
)
engine = create_async_engine(
    database_url,
    echo=True,
    pool_size=5,
    max_overflow=10
)



