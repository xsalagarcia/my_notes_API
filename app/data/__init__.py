import os
from redis import Redis
from sqlmodel import create_engine, SQLModel

from app.settings.settings import settings

redis_data = Redis(host=settings.redis_host,
                   port=settings.redis_port,
                   password=settings.redis_password,
                   decode_responses=True)

engine = create_engine(url=settings.sql_database_url if os.getenv("IN_MEMORY_DB") is None else "sqlite://",
                       **settings.database_settings.model_dump() if os.getenv(
                           "IN_MEMORY_DB") is None else {})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def restart_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    create_db_and_tables()