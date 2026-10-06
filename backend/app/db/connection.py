from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.pool import NullPool

from app.core.config import get_settings


def database_url() -> URL:
    value = get_settings().database_url.get_secret_value()
    if not value:
        raise ValueError("DATABASE_URL is not configured.")
    url = make_url(value)
    if url.drivername not in ("postgres", "postgresql", "postgresql+psycopg"):
        raise ValueError("DATABASE_URL must be a PostgreSQL connection URL.")
    return url.set(drivername="postgresql+psycopg")


@lru_cache
def get_engine() -> Engine:
    # Supabase owns pooling; disable prepared statements for transaction-pooler use.
    return create_engine(
        database_url(),
        poolclass=NullPool,
        connect_args={"prepare_threshold": None, "connect_timeout": 10},
    )
