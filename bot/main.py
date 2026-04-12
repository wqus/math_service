import asyncio
from database.engine import engine
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp.web_app import Application

from infrastucture.llm_client import MathAIClient
from repositories.admins_repository import AdminRepository
from repositories.banned_users_repository import BannedRepository
from repositories.history_repository import HistoryRepository
from repositories.stars_transactions_repository import PaymentsRepository
from repositories.support_messages_repository import TicketRepository
from repositories.users_repository import UserRepository
from services.AIService import AIService
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
from core.config import LOCAL_WEBHOOK_PORT, LOCAL_WEBHOOK_HOST, WEBHOOK_PATH, LLM_URL
from core.config import MODE


async def main():
    """
    Главная функция запуска бота.
    Настраивает вебхук, middleware и запускает сервер.
    """
    logger = init_log()

    try:
        # Инициализация бота, диспетчера и Redis клиента
        logger.info("ШАГ 1: Инициализация бота...")
        bot, dp, redis_client = await init_bot()
        logger.info("Бот инициализирован")

        logger.debug("Создание web.Application")
        app = web.Application()

        logger.info("Настройка middleware")
        dp.message.outer_middleware(InjectLanguage())
        dp.callback_query.outer_middleware(InjectLanguage())
        dp.message.outer_middleware(IntentMiddleware())
        logger.info("Middleware настроены")

        # Загрузка текстовых сообщений
        logger.info("ШАГ 2: Загрузка текстов...")
        dp['texts'] = await load_texts()
        logger.info("Тексты загружены")

        # Инициализация
        llm_client = MathAIClient(api_url=LLM_URL)

        # Инициализация репозиториев
        logger.info("ШАГ 3: Инициализация репозиториев...")
        admins_repo = AdminRepository(engine=engine)
        ban_repo = BannedRepository(engine=engine)
        history_repo = HistoryRepository(engine=engine)
        payments_repo = PaymentsRepository(engine=engine)
        ticket_repo = TicketRepository(engine=engine)
        users_repo = UserRepository(engine=engine)
        logger.info("Репозитории инициализированы")

        # Инициализация сервисов
        logger.info("ШАГ 4: Инициализация сервисов...")
        cache = CacheService(redis_client=redis_client)
        access_service = AccessService(users_repo=users_repo, ban_repo=ban_repo, admins_repo=admins_repo,
                                       cache=cache)
        admin_service = AdminService(ticket_repo=ticket_repo, ban_repo=ban_repo)
        history_service = HistoryService(repo=history_repo)
        payments_service = PaymentsService(repo=payments_repo)
        user_service = UserService(repo=users_repo)
        ai_service = AIService(llm_client= llm_client)
        logger.info("Сервисы инициализированы")

        # Регистрация сервисов в диспетчере
        dp['access_service'] = access_service
        dp['admin_service'] = admin_service
        dp['history_service'] = history_service
        dp['payments_service'] = payments_service
        dp['user_service'] = user_service
        dp['ai_service'] = ai_service
        # Инициализация
        llm_client = MathAIClient(api_url=LLM_URL)
        dp['llm_client'] = llm_client


        logger.info("ШАГ 5: Регистрация startup/shutdown...")
        dp.startup.register(startup)
        dp.shutdown.register(shutdown)
        logger.info("Startup/shutdown зарегистрированы")

        if MODE == 'dev':
            logger.info("ЗАПУСК В РЕЖИМЕ POLLING")
            await dp.start_polling(bot)
        else:
            logger.info("ЗАПУСК В РЕЖИМЕ WEBHOOK")
            logger.info("Регистрация SimpleRequestHandler")
            SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
            logger.info(f"SimpleRequestHandler зарегистрирован на пути {WEBHOOK_PATH}")

            # Обертки для передачи dp startup в web app
            async def on_startup(app: Application):
                """
                Запускает startup-функции диспетчера при старте приложения.
                """
                logger.info("=" * 60)
                logger.info("ВЫЗВАНА on_startup (обертка)")
                logger.info("Вызываю dp.emit_startup()...")
                await dp.emit_startup(bot)
                logger.info("dp.emit_startup() выполнен")
                logger.info("=" * 60)

            async def on_shutdown(app: Application):
                """
                Запускает shutdown-функции диспетчера при остановке приложения.
                """
                logger.info("=" * 60)
                logger.info("ВЫЗВАНА on_shutdown (обертка)")
                logger.info("Вызываю dp.emit_shutdown()...")
                await dp.emit_shutdown(bot)
                logger.info("dp.emit_shutdown() выполнен")
                logger.info("=" * 60)
                await llm_client.close()

            app.on_startup(on_startup)
            app.on_shutdown(on_shutdown)
            logger.info("Обертки on_startup/on_shutdown зарегистрированы")

            # Запуск сервера
            logger.info(f"ШАГ 6: Запуск веб-сервера на {LOCAL_WEBHOOK_HOST}:{LOCAL_WEBHOOK_PORT}")
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner=runner, host=LOCAL_WEBHOOK_HOST, port=LOCAL_WEBHOOK_PORT)

            await site.start()
            logger.info("ВЕБ-СЕРВЕР ЗАПУЩЕН. Ожидание запросов...")
            await asyncio.Future()
    except Exception as e:
        logger.critical(f"Ошибка при работе main функции: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())