from aiogram.fsm.storage.redis import RedisStorage
from config import TOKEN
from aiogram import Bot, Dispatcher
from middlewares.user_language import InjectLanguage
from handlers.admin import router as admin_router
from handlers.common import router as common_router
from handlers.user import router as user_router
from startup import storage

bot = Bot(token=TOKEN)  # создаем экземпляр бота
dp = Dispatcher(storage=storage)

middleware = InjectLanguage(db_path="bot_data.db")
dp.message.middleware(middleware)
dp.callback_query.middleware(middleware)

dp.include_router(admin_router)
dp.include_router(common_router)
dp.include_router(user_router)


