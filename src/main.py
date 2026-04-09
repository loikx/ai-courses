import logging
import os
from datetime import date, datetime
from uuid import uuid4, UUID
from fastapi import FastAPI, Path, HTTPException, Body, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic_settings import BaseSettings
from .history_models import WeatherHistoryResponse
from .history_repository import HistoryRepository
from .history_service import HistoryService, HistoryValidationError
from .models import (
    WeatherResponse,
    SubscribeRequest,
    SubscriptionData,
    SubscriptionResponse,
    SubscriptionsListResponse,
)
from .weather_client import WeatherClient, CityNotFound, WeatherProviderError
from .database import get_db, engine
from .db_models import Base
from .repository import SubscriptionRepository

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Настройки приложения"""
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
    mock_history_enabled: bool = os.getenv("MOCK_HISTORY_ENABLED", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
logger.info(f"Application started with API key: {settings.openweather_api_key}")
weather_client = WeatherClient(
    api_key=settings.openweather_api_key,
    mock_history_enabled=settings.mock_history_enabled,
)

# Создание таблиц при запуске приложения
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WeatherApp",
    description="API для получения информации о погоде",
    version="1.0.0"
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "ok"}


@app.get("/weather/{city}", response_model=WeatherResponse, tags=["Weather"])
async def get_weather(
    city: str = Path(..., min_length=1, max_length=100, description="Название города")
) -> WeatherResponse:
    """
    Получить информацию о погоде для города
    
    - **city**: Название города (обязательно)
    
    Возвращает:
    - Температуру в градусах Цельсия
    - Условия погоды
    - Влажность
    - Скорость ветра
    - Давление
    """
    logger.info(f"GET /weather/{city}")
    
    try:
        # Нормализация названия города
        city_normalized = city.strip()
        
        # Получение данных о погоде
        weather_data = weather_client.get_weather(city_normalized)
        
        return WeatherResponse(
            success=True,
            data=weather_data,
            error=None
        )
    
    except CityNotFound as e:
        logger.error(f"City not found: {city}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except WeatherProviderError as e:
        logger.error(f"Weather provider error: {e}")
        raise HTTPException(status_code=503, detail="Weather service temporarily unavailable")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get(
    "/weather/{city}/history",
    response_model=WeatherHistoryResponse,
    tags=["Weather"],
)
async def get_weather_history(
    city: str = Path(..., min_length=1, max_length=100, description="Название города"),
    start_date: date = Query(..., description="Начальная дата диапазона"),
    end_date: date = Query(..., description="Конечная дата диапазона"),
    db: Session = Depends(get_db),
) -> WeatherHistoryResponse:
    """Получить историю погоды по городу за диапазон дат."""
    logger.info(
        "GET /weather/%s/history start_date=%s end_date=%s",
        city,
        start_date,
        end_date,
    )

    service = HistoryService(
        repository=HistoryRepository(db),
        weather_client=weather_client,
    )

    try:
        history_data = service.get_history(
            city=city,
            start_date=start_date,
            end_date=end_date,
        )
        logger.info(
            "History response ready city=%s start_date=%s end_date=%s records=%s",
            history_data.city,
            history_data.start_date,
            history_data.end_date,
            len(history_data.records),
        )
        return WeatherHistoryResponse(success=True, data=history_data, error=None)

    except CityNotFound as e:
        logger.error(f"City not found: {city}")
        raise HTTPException(status_code=400, detail=str(e))

    except WeatherProviderError as e:
        logger.error(f"Weather provider error: {e}")
        raise HTTPException(status_code=503, detail="Weather service temporarily unavailable")

    except HistoryValidationError as e:
        logger.error(f"Invalid history request: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error while getting history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/subribe/{city}", response_model=SubscriptionResponse, status_code=201, tags=["Subscriptions"])
async def subscribe_to_city(
    city: str = Path(..., min_length=1, max_length=100, description="Название города"),
    request: SubscribeRequest = Body(...),
    db: Session = Depends(get_db),
) -> SubscriptionResponse:
    """
    Создать подписку на уведомления о погоде для города.

    Подписки хранятся в PostgreSQL.
    """
    logger.info(f"POST /subribe/{city}")

    city_normalized = " ".join(city.strip().split())
    repository = SubscriptionRepository(db)

    existing_subscription = repository.get_by_email_and_city(
        email=request.email,
        city=city_normalized,
    )
    if existing_subscription is not None:
        logger.error(f"Subscription already exists: {request.email}:{city_normalized}")
        raise HTTPException(status_code=409, detail="Subscription already exists")

    try:
        # Проверяем, что город существует, через провайдера погоды.
        weather_client.get_weather(city_normalized)
    except CityNotFound as e:
        logger.error(f"City not found for subscription: {city_normalized}")
        raise HTTPException(status_code=400, detail=str(e))
    except WeatherProviderError as e:
        logger.error(f"Weather provider error during subscription: {e}")
        raise HTTPException(status_code=503, detail="Weather service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error during subscription: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    try:
        # Создание подписки в БД
        subscription = repository.create(email=request.email, city=city_normalized)
        logger.info(f"Subscription created: {subscription.id}")
        
        return SubscriptionResponse(success=True, data=subscription, error=None)
    
    except IntegrityError:
        logger.error(f"Subscription already exists: {request.email}:{city_normalized}")
        raise HTTPException(status_code=409, detail="Subscription already exists")
    
    except Exception as e:
        logger.error(f"Unexpected error during subscription creation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/subscribe/{id}", response_model=SubscriptionResponse, tags=["Subscriptions"])
async def delete_subscription(
    id: str = Path(..., min_length=1, description="ID подписки"),
    db: Session = Depends(get_db),
) -> SubscriptionResponse:
    """
    Удалить подписку по ID.
    
    - **id**: Уникальный идентификатор подписки (обязательно)
    
    Возвращает:
    - Удалённую подписку при успехе
    - 404 ошибку, если подписка не найдена
    """
    logger.info(f"DELETE /subscribe/{id}")
    
    try:
        # Преобразование строки в UUID
        try:
            subscription_id = UUID(id)
        except ValueError:
            logger.error(f"Invalid UUID format: {id}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid subscription ID format"
            )
        
        # Удаление подписки из БД
        repository = SubscriptionRepository(db)
        subscription = repository.delete(subscription_id)
        
        if not subscription:
            logger.error(f"Subscription not found: {id}")
            raise HTTPException(
                status_code=404,
                detail=f"Subscription with id '{id}' not found"
            )
        
        logger.info(f"Subscription deleted: {id}")
        return SubscriptionResponse(success=True, data=subscription, error=None)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error during deletion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/subscriptions", response_model=SubscriptionsListResponse, tags=["Subscriptions"])
async def get_subscriptions(db: Session = Depends(get_db)) -> SubscriptionsListResponse:
    """
    Получить все подписки.
    
    Возвращает:
    - Список всех активных подписок
    - Пустой список, если подписок нет
    """
    logger.info("GET /subscriptions")
    
    try:
        repository = SubscriptionRepository(db)
        subscriptions = repository.get_all()
        logger.info(f"Returned {len(subscriptions)} subscriptions")
        
        return SubscriptionsListResponse(success=True, data=subscriptions, error=None)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
