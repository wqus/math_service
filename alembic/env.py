import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config
fileConfig(config.config_file_name)

POSTGRES_USER = os.getenv("POSTGRES_USER", "bot")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "botpass")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "bot_db")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

def run_migrations_offline():
    """Запуск миграций в offline-режиме"""
    context.configure(url=DATABASE_URL, target_metadata=None, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Запуск миграций онлайн"""
    connectable = create_async_engine(DATABASE_URL, poolclass=asyncio.pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())