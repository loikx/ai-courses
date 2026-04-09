"""SQLAlchemy ORM модели для базы данных."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

# Base для всех моделей
Base = declarative_base()


class Subscription(Base):
    """
    ORM модель для подписок на уведомления о погоде.
    
    Атрибуты:
        id: UUID первичный ключ
        email: Email подписчика
        city: Город для подписки
        created_at: Время создания подписки
        updated_at: Время последнего обновления
    """
    __tablename__ = "subscriptions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )
    email = Column(String(255), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Уникальное ограничение на (email, city) для предотвращения дублей
    __table_args__ = (
        UniqueConstraint('email', 'city', name='uq_subscription_email_city'),
        Index('idx_subscriptions_email', 'email'),
        Index('idx_subscriptions_city', 'city'),
    )

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, email={self.email}, city={self.city})>"


class StoredHistoricalWeather(Base):
    """ORM модель для сохранённой дневной истории погоды."""

    __tablename__ = "weather_history"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
    )
    city = Column(String(100), nullable=False, index=True)
    date = Column(Date, nullable=False)
    temp = Column(Float, nullable=False)
    condition = Column(String(100), nullable=False)
    humidity = Column(Integer, nullable=False)
    wind_speed = Column(Float, nullable=False)
    pressure = Column(Integer, nullable=False)
    fetched_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint("city", "date", name="uq_weather_history_city_date"),
        Index("idx_weather_history_city_date", "city", "date"),
    )

    def __repr__(self) -> str:
        return (
            "StoredHistoricalWeather("
            f"id={self.id}, city={self.city}, date={self.date}"
            ")"
        )
