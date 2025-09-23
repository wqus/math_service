import asyncio
import matplotlib
from botMath import bot, dp
from startup import init_redis, init_bot_db, init_history_db, close_redis

redis_cl = None
async def main(): #функция при запуске
    await init_redis(dp)
    matplotlib.use('Agg')
    dp.startup.register(init_bot_db)
    dp.startup.register(init_history_db)
    dp.shutdown.register(close_redis)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
