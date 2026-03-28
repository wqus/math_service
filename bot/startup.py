import json
from logging.handlers import RotatingFileHandler

import aiofiles
import redis.asyncio as redis
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.redis import RedisStorage
import logging
from core.config import WEBHOOK_URL_FULL_PATH
import matplotlib
from core.config import TOKEN, MODE
from aiogram import Bot, Dispatcher
from handlers.admin import router as admin_router
from handlers.common import router as common_router
from handlers.user import router as user_router
from handlers.payments import router as payments_router
from aiogram.client.session.aiohttp import AiohttpSession

logger = logging.getLogger(name=__name__)


async def init_bot():
    """
    Инициализирует бота, диспетчер и Redis клиент.
    """
    try:
        session = AiohttpSession()

        logger.info("Инициализация бота")
        bot = Bot(token=TOKEN, session=session)

        logger.info("Подключение к Redis")
        redis_client = await init_redis()

        logger.debug("Создание RedisStorage")
        storage = RedisStorage(redis_client, data_ttl=600, state_ttl=600)

        logger.debug("Создание Dispatcher")
        dp = Dispatcher(storage=storage)

        logger.info("Подключение роутеров")
        dp.include_routers(admin_router, common_router, user_router, payments_router)
        return bot, dp, redis_client
    except Exception:
        logger.critical("Не удалось запустить бота — критическая ошибка инициализации", exc_info=True)
        raise


def init_log():
    """
    Настраивает логирование с ротацией файлов и выводом в консоль.
    """
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return None
    root_logger.setLevel(logging.DEBUG)
    root_logger.propagate = True
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')

    # Хендлер для записи в файл с ограничением размера и количества лог-файлов
    file_handler = RotatingFileHandler(
        'bot/logs/bot.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Хендлер для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    return root_logger


async def init_redis():
    """
    Устанавливает соединение с Redis.
    """
    try:
        logger.info("Создание Redis клиента")
        redis_client = await redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            max_connections=25,
            health_check_interval=30,
            socket_timeout=4
        )
        return redis_client
    except Exception:
        logger.error("Ошибка создания Redis клиента")
        raise


async def close_redis(redis_client, dispatcher: Dispatcher):
    """
    Закрывает соединение с Redis.
    """
    try:
        if redis_client:
            logger.info("Закрытие Redis клиента")
            await redis_client.close()
    except Exception:
        logger.error("Ошибка при закрытии Redis клиента")


async def startup(bot: Bot):
    """
    Выполняет настройку при старте бота.
    """
    matplotlib.use('Agg')
    if MODE != 'dev':
        await bot.set_webhook(url=WEBHOOK_URL_FULL_PATH)


async def shutdown(bot: Bot, dp, redis_client):
    """
    Выполняет завершение работы бота.
    """
    await close_redis(redis_client=redis_client, dispatcher=dp)
    await bot.session.close()
    if MODE != 'dev':
        await bot.delete_webhook()


async def load_texts():
    """
    Загружает текстовые ресурсы для локализации.
    """
    try:
        logging.info("Загрузка текстовых ресурсов")
        async with aiofiles.open('D:\\Python_project\\Math_Bot\\bot\\locales\\text_ru.json', 'r', encoding='utf-8') as ru_file:
            ru_content = await ru_file.read()
            texts_ru = json.loads(ru_content)

        async with aiofiles.open('D:\\Python_project\\Math_Bot\\bot\\locales\\text_en.json', 'r', encoding='utf-8') as en_file:
            en_content = await en_file.read()
            texts_en = json.loads(en_content)

        return {'language:RU': texts_ru, 'language:EN': texts_en}
    except FileNotFoundError:
        logger.error("Ошибка загрузки текстовых ресурсов")
        raise