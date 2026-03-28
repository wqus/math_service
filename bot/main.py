import asyncio
from database.engine import engine
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp.web_app import Application

from repositories.admins_repository import AdminRepository
from repositories.banned_users_repository import BannedRepository
from repositories.history_repository import HistoryRepository
from repositories.stars_transactions_repository import PaymentsRepository
from repositories.support_messages_repository import TicketRepository
from repositories.users_repository import UserRepository
from services.AccessService import AccessService
from services.AdminService import AdminService
from services.CaсheService import CacheService
from services.HistoryService import HistoryService
from services.PaymentsService import PaymentsService
from services.UserService import UserService
from startup import shutdown, startup, init_bot, load_texts, init_log
from aiohttp import web
from middlewares.user_language import InjectLanguage
from middlewares.IntentMW import IntentMiddleware
from core.config import WEBHOOK_PATH, LOCAL_WEBHOOK_PORT, LOCAL_WEBHOOK_HOST
from core.config import MODE

async def main():
    """
    Главная функция запуска бота.
    Настраивает вебхук, middleware и запускает сервер.
    """
    logger = init_log()
    try:
        # Инициализация бота, диспетчера и Redis клиента
        bot, dp, redis_client = await init_bot()

        logger.debug("Создание web.Application")
        app = web.Application()

        logger.info("Настройка middleware")
        dp.message.outer_middleware(InjectLanguage())
        dp.callback_query.outer_middleware(InjectLanguage())
        dp.message.outer_middleware(IntentMiddleware())

        # Загрузка текстовых сообщений
        dp['texts'] = await load_texts()

        # Инициализация репозиториев
        admins_repo = AdminRepository(engine=engine)
        ban_repo = BannedRepository(engine=engine)
        history_repo = HistoryRepository(engine=engine)
        payments_repo = PaymentsRepository(engine=engine)
        ticket_repo = TicketRepository(engine=engine)
        users_repo = UserRepository(engine=engine)

        # Инициализация сервисов
        cache = CacheService(redis_client=redis_client)
        access_service = AccessService(users_repo=users_repo, ban_repo=ban_repo, admins_repo=admins_repo,
                                       cache=cache)
        admin_service = AdminService(ticket_repo=ticket_repo, ban_repo=ban_repo)
        history_service = HistoryService(repo=history_repo)
        payments_service = PaymentsService(repo=payments_repo)
        user_service = UserService(users_repo)

        # Регистрация сервисов в диспетчере
        dp['access_service'] = access_service
        dp['admin_service'] = admin_service
        dp['history_service'] = history_service
        dp['payments_service'] = payments_service
        dp['user_service'] = user_service

        dp.startup.register(startup)
        dp.shutdown.register(shutdown)

        if MODE == 'dev':
            await dp.start_polling(bot)
        else:
            logger.info("Регистрация SimpleRequestHandler")
            SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

            # Обертки для передачи dp startup в web app
            async def on_startup(app: Application):
                """
                Запускает startup-функции диспетчера при старте приложения.
                """
                logger.info("Запуск startup функций диспетчера")
                await dp.emit_startup(bot)

            async def on_shutdown(app: Application):
                """
                Запускает shutdown-функции диспетчера при остановке приложения.
                """
                logger.info("Запуск shutdown функций диспетчера")
                await dp.emit_shutdown(bot)

            app.on_startup(on_startup)
            app.on_shutdown(on_shutdown)

            # Запуск сервера
            logger.info("Запуск веб-сервера")
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner=runner, host=LOCAL_WEBHOOK_HOST, port=LOCAL_WEBHOOK_PORT)

            await site.start()
            await asyncio.Future()
    except Exception as e:
        logger.critical("Ошибка при работе main функции: %s", e)
        raise

