"""
Конфигурация подключения к базе данных PostgreSQL.

Этот модуль содержит:
- Инициализацию SQLAlchemy engine
- Создание SessionLocal для работы с БД
- Функцию get_db() для dependency injection в FastAPI
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

# Получение DATABASE_URL из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://weather_user:weather_password@localhost:5432/weather_db"
)

# Создание engine
# NullPool используется для избежания проблем с соединениями в асинхронном контексте
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False  # Установите True для отладки SQL запросов
)

# Создание SessionLocal для работы с БД
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Session:
    """
    Dependency injection для получения сессии БД в FastAPI endpoints.
    
    Использование:
        @app.get("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            ...
    
    Yields:
        Session: Сессия SQLAlchemy для работы с БД
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
