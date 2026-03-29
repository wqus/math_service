from sqlalchemy.ext.asyncio import create_async_engine

database_url = (
    "postgresql+asyncpg://bot:botpass@postgres:5432/bot_db"
)
engine = create_async_engine(
    database_url,
    echo=True,
    pool_size=5,
    max_overflow=10
)