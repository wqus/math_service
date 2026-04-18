from sqlalchemy.ext.asyncio import create_async_engine
from bot.core.config import POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
database_url = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
)
engine = create_async_engine(
    database_url,
    echo=True,
    pool_size=5,
    max_overflow=10
)