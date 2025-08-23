import asyncio

import matplotlib
from botMath import bot, init_dp
from startup import init_redis, init_db

redis_cl = None
async def main(): #функция при запуске
    redis_client = await init_redis(redis_cl)

    dp = await init_dp(redis_client)
    matplotlib.use('Agg')
    dp.startup.register(init_db)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
