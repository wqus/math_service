import asyncio
import matplotlib
from botMath import bot, dp
from startup import init_redis, close_redis

redis_cl = None
async def main(): #функция при запуске
    await init_redis(dp)
    matplotlib.use('Agg')
    dp.shutdown.register(close_redis)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
