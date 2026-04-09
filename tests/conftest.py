import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


TEST_DATABASE_PATH = Path("/tmp/practice_03_test_history.db")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DATABASE_PATH}")
os.environ.setdefault("OPENWEATHER_API_KEY", "test-api-key")

from src.database import get_db
from src.db_models import Base
from src.main import app


engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_database() -> None:
    """Пересоздаёт схему между тестами для изоляции history-сценариев."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session() -> Session:
    """Возвращает отдельную SQLAlchemy-сессию для проверок в тестах."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client() -> TestClient:
    """Подменяет dependency на тестовую БД и возвращает TestClient."""

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
