from aiogram.fsm.storage.redis import RedisStorage
from config import TOKEN
from aiogram import Bot, Dispatcher
from middlewares.user_language import InjectLanguage
from handlers.admin import router as admin_router
from handlers.common import router as common_router
from handlers.user import router as user_router

bot = Bot(token=TOKEN)  # создаем экземпляр бота

async def init_dp(redis_cl):
    dp = Dispatcher(storage=RedisStorage(redis=redis_cl))
    middleware = InjectLanguage(db_path="bot_data.db")
    dp.message.middleware(middleware)

    # add router
    dp.include_router(admin_router)
    dp.include_router(common_router)
    dp.include_router(user_router)
    return dp


