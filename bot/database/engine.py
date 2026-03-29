from sqlalchemy.ext.asyncio import create_async_engine
from core.config import POSTGRES_HOST
database_url = (
    f"postgresql+asyncpg://bot:botpass@{POSTGRES_HOST}:5432/bot_db"
)
engine = create_async_engine(
    database_url,
    echo=True,
    pool_size=5,
    max_overflow=10
)