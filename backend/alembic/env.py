
from logging.config import fileConfig

from alembic import context

from app.core.database import Base, engine

# Import all models so SQLAlchemy registers their tables
from app.models import (
    Session,
    Frame,
    Detection,
    OCRResult,
    Question,
    Answer,
)

# Alembic configuration
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Register all model metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without opening a database connection."""

    context.configure(
        url=engine.url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using the existing database engine."""

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
