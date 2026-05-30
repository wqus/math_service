from dotenv import load_dotenv
import os

import pytest_asyncio

from alembic.config import Config
from alembic import command

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv(".env.test")

DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}/"
    f"{os.getenv('POSTGRES_DB')}"
)


@pytest_asyncio.fixture
async def engine():
    cfg = Config("alembic.ini")
    cfg.set_main_option(
        "sqlalchemy.url",
        DATABASE_URL.replace("+asyncpg", "")
    )

    command.upgrade(cfg, "head")

    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        await conn.execute(text("""
            TRUNCATE TABLE
                support_messages,
                stars_transactions,
                banned_users,
                history,
                users
            RESTART IDENTITY CASCADE
        """))

    yield engine

    await engine.dispose()