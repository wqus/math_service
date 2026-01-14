import json
from logging.handlers import RotatingFileHandler

import aiofiles
import redis.asyncio as redis
from aiogram.fsm.storage.redis import RedisStorage
import logging

from config import WEBHOOK_URL_FULL_PATH
import matplotlib
from config import TOKEN
from aiogram import Bot, Dispatcher
from handlers.admin import router as admin_router
from handlers.common import router as common_router
from handlers.user import router as user_router
from aiogram.client.session.aiohttp import AiohttpSession

logger = logging.getLogger(name = __name__)

async def init_bot():
    try:
        #Создаем сессию
        logger.debug("Сессия создана")
        session = AiohttpSession()

        logger.info("Инициализация бота")
        bot = Bot(token=TOKEN, session=session)  # создаем экземпляр бота

        logger.info("Подключение к Redis")
        redis_client = await init_redis()

        logger.debug("Создаем RedisStorage")
        storage = RedisStorage(redis_client)

        logger.debug("Создаем Dispatcher")
        dp = Dispatcher(storage=storage)

        logger.info("Подключение роутеров")
        dp.include_router(admin_router)
        dp.include_router(common_router)
        dp.include_router(user_router)
        return bot, dp
    except Exception:
        logger.critical("Не удалось запустить бота — критическая ошибка инициализации", exc_info=True)
        raise

def init_log():
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return None
    root_logger.setLevel(logging.DEBUG)
    root_logger.propagate = True
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')

    #Хендлер для записи в файл с ограничением размера и количества лог-файлов
    handler = RotatingFileHandler(
        'logs/bot.log',
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )

    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)

    #Хендлер для вывода в консоль.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    return root_logger

async def init_redis(): #устанавливает соединение с редис
    try:
        logger.info("Создание redis_client")
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, max_connections=25,
                                   health_check_interval=30, socket_timeout=4)
        return redis_client
    except Exception:
        logger.error("Ошибка создания redis_client")
        raise

async def close_redis(redis_client, dispatcher: Dispatcher):  # on_shutdown, закрывает соединение с редис
    try:
        if redis_client:
            logger.info("Закрытие redis_client")
            await redis_client.close
    except Exception:
        logger.error("Ошибка при закрытие redis_client")

#webhook register
async def webhook_startup(bot: Bot):
    try:
        matplotlib.use('Agg')
        logger.info("Установка webhook")
        await bot.set_webhook(url = WEBHOOK_URL_FULL_PATH)
    except Exception:
        logger.exception("Ошибка при работе webhook_startup")
        raise

async def webhook_shutdown(bot, dp, redis_client):
    try:
        logger.info("Процесс работы webhook_shutdown")
        await close_redis(redis_client=redis_client, dispatcher=dp)
        await bot.delete_webhook()
        await bot.session.close()
    except Exception:
        logger.exception("Ошибка при работе функции webhook_shutdown")

#1. Загрузка текстовых ресурсов
async def load_texts():
    try:
        logging.info("Загрузка текстов")
        async with aiofiles.open('D:\\Python_project\\Math_Bot\\text_ru.json', 'r', encoding='utf-8') as f:
            ru_content = await f.read()
            texts_ru = json.loads(ru_content)
        async with aiofiles.open('D:\\Python_project\\Math_Bot\\text_en.json', 'r', encoding='utf-8') as f:
            en_content = await f.read()
            texts_en = json.loads(en_content)
        return {'language:RU': texts_ru, 'language:EN': texts_en}
    except FileNotFoundError:
        logger.error("Ошибка загрузки текстов")
        raise

