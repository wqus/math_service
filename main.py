import asyncio

from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp.web_app import Application
from sympy.stats import Expectation

from startup import webhook_shutdown, webhook_startup, init_bot, load_texts, init_log
from aiohttp import web
from middlewares.user_language import InjectLanguage
from middlewares.IntentMW import IntentMiddleware
from config import WEBHOOK_PATH, LOCAL_WEBHOOK_PORT, LOCAL_WEBHOOK_HOST


async def main():
    logger = init_log()
    try:

        bot, dp = await init_bot()

        logger.debug("Создание web.Application")
        app = web.Application()

        logger.info("Настройка middleware's")
        dp.message.outer_middleware(InjectLanguage())
        dp.callback_query.outer_middleware(InjectLanguage())
        dp.message.outer_middleware(IntentMiddleware())

        dp['texts'] = await load_texts()
        
        logger.info("Регистрация SimpleRequestHandler")
        SimpleRequestHandler(dispatcher=dp, bot = bot).register(app, path = WEBHOOK_PATH)
        dp.startup.register(webhook_startup)
        dp.shutdown.register(webhook_shutdown)

        #обертки для передачи dp startup в web app
        async def on_startup(app: Application):
            logger.info("Startup dp функций")
            await dp.emit_startup(bot)

        async def on_shutdown(app: Application):
            logger.info("Shutdown dp функций")
            await dp.emit_shutdown(bot)

        app.on_startup(on_startup)
        app.on_shutdown(on_shutdown)

        #запуск сервера
        logger.info("Запуск сервера")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner=runner, host = LOCAL_WEBHOOK_HOST, port = LOCAL_WEBHOOK_PORT)

        await site.start()
        await asyncio.Future()
    except Expectation as e:
        logger.critical("Ошибка при работе main функции: %s", e)
        raise

if __name__ == '__main__':
    asyncio.run(main())
