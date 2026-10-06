from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.db.connection import database_url


if context.is_offline_mode():
    # Offline SQL compilation needs no project credentials or connection.
    context.configure(
        dialect_name="postgresql",
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(
        database_url(),
        poolclass=NullPool,
        connect_args={"prepare_threshold": None, "connect_timeout": 10},
    )
    try:
        with engine.connect() as connection:
            context.configure(connection=connection)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()
