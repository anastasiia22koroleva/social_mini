# social_mini/database.py
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

# Берём URL из переменной окружения (Docker) или используем локальный по умолчанию
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost/social_mini"
)

# Асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool,
)

# Фабрика сессий
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ЕДИНАЯ Base для всех моделей
Base = declarative_base()


async def get_db():
    """
    Зависимость FastAPI: отдаёт асинхронную сессию БД.
    """
    async with async_session_maker() as session:
        yield session