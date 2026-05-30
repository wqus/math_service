import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

config = context.config
fileConfig(config.config_file_name)

DATABASE_URL = config.get_main_option("sqlalchemy.url")

if not DATABASE_URL or DATABASE_URL == "dummy":
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"


def run_migrations_offline():
    context.configure(url=DATABASE_URL, target_metadata=None, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(DATABASE_URL)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
