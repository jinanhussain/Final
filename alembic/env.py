import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.models.user_model import Base  # Replace with the actual location of your models

# this is the Alembic Config object, which provides access to the values within the .ini file
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name:
    fileConfig(config.config_file_name)

# Replace target_metadata with the Base metadata of your models
target_metadata = Base.metadata


# Async migrations
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper function for running migrations online."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using async engine."""
    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"))

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
