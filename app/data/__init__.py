import os
from redis import Redis
from sqlalchemy import Engine, event
from sqlmodel import create_engine, SQLModel

from app.settings.settings import settings
#tables
from app.models.category import Category
from app.models.tag import Tag

redis_data = Redis(host=settings.redis_host,
                   port=settings.redis_port,
                   password=settings.redis_password,
                   decode_responses=True)

engine = create_engine(url=settings.sql_database_url if os.getenv("IN_MEMORY_DB") is None else "sqlite://",
                       **settings.database_settings.model_dump() if os.getenv(
                           "IN_MEMORY_DB") is None else {})

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    This enables foreign key enforcement for sqlite.
    :param dbapi_connection:
    :param connection_record:
    :return:
    """
    if settings.sql_database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def restart_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    create_db_and_tables()