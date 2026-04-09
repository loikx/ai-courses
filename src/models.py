import re
from datetime import datetime
from pydantic import BaseModel, field_validator


class WeatherData(BaseModel):
    """Модель данных о погоде"""
    city: str
    temp: float
    condition: str
    humidity: int
    wind_speed: float
    pressure: int
    fetched_at: datetime


class WeatherResponse(BaseModel):
    """Ответ API"""
    success: bool
    data: WeatherData | None = None
    error: str | None = None


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class SubscribeRequest(BaseModel):
    """Запрос на подписку"""
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Базовая валидация email без внешних зависимостей"""
        email = value.strip().lower()
        if not EMAIL_REGEX.fullmatch(email):
            raise ValueError("Invalid email format")
        return email


class SubscriptionData(BaseModel):
    """Модель подписки"""
    id: str
    city: str
    email: str
    created_at: datetime


class SubscriptionResponse(BaseModel):
    """Ответ API для подписки"""
    success: bool
    data: SubscriptionData | None = None
    error: str | None = None


class SubscriptionsListResponse(BaseModel):
    """Ответ API для списка подписок"""
    success: bool
    data: list[SubscriptionData] = []
    error: str | None = None
