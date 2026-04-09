import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.models import WeatherData
from src.weather_client import CityNotFound, WeatherProviderError
from src.database import get_db
from src.db_models import Base

# Создание тестовой БД в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override get_db для использования тестовой БД"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_database():
    """Очистка БД между тестами"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestWeatherEndpointSuccess:
    """Тесты успешных запросов"""
    
    @patch('src.main.weather_client.get_weather')
    def test_get_weather_success(self, mock_get_weather):
        """Успешное получение погоды"""
        mock_get_weather.return_value = WeatherData(
            city="London",
            temp=15.5,
            condition="Cloudy",
            humidity=70,
            wind_speed=5.2,
            pressure=1013,
            fetched_at=datetime.now()
        )
        
        response = client.get("/weather/London")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["city"] == "London"
        assert data["data"]["temp"] == 15.5
        assert data["error"] is None
    
    @patch('src.main.weather_client.get_weather')
    def test_get_weather_with_spaces(self, mock_get_weather):
        """Получение погоды с пробелами в названии"""
        mock_get_weather.return_value = WeatherData(
            city="New York",
            temp=20.0,
            condition="Clear",
            humidity=60,
            wind_speed=3.0,
            pressure=1015,
            fetched_at=datetime.now()
        )
        
        response = client.get("/weather/New%20York")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestWeatherEndpointErrors:
    """Тесты обработки ошибок"""
    
    @patch('src.main.weather_client.get_weather')
    def test_city_not_found_400(self, mock_get_weather):
        """Город не найден - 400"""
        mock_get_weather.side_effect = CityNotFound("City 'InvalidCity' not found")
        
        response = client.get("/weather/InvalidCity")
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    @patch('src.main.weather_client.get_weather')
    def test_weather_provider_error_503(self, mock_get_weather):
        """Ошибка API - 503"""
        mock_get_weather.side_effect = WeatherProviderError("Weather API error: 401")
        
        response = client.get("/weather/London")
        assert response.status_code == 503
        assert "temporarily unavailable" in response.json()["detail"].lower()
    
    @patch('src.main.weather_client.get_weather')
    def test_unexpected_error_500(self, mock_get_weather):
        """Неожиданная ошибка - 500"""
        mock_get_weather.side_effect = Exception("Unexpected error")
        
        response = client.get("/weather/London")
        assert response.status_code == 500


class TestWeatherEndpointValidation:
    """Тесты валидации параметров"""
    
    def test_city_parameter_required(self):
        """Параметр city обязателен"""
        response = client.get("/weather/")
        assert response.status_code == 404
    
    def test_city_parameter_max_length(self):
        """Максимальная длина города"""
        long_city = "a" * 101
        response = client.get(f"/weather/{long_city}")
        assert response.status_code == 422
    
    def test_city_parameter_min_length(self):
        """Минимальная длина города"""
        response = client.get("/weather/")
        assert response.status_code == 404


class TestHealthCheck:
    """Тесты health check"""
    
    def test_health_check(self):
        """Проверка здоровья приложения"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestSubscribeEndpoint:
    """Тесты POST /subscribe/{city}"""

    @patch('src.main.weather_client.get_weather')
    def test_subscribe_success(self, mock_get_weather):
        """Успешная подписка на город"""
        mock_get_weather.return_value = WeatherData(
            city="London",
            temp=15.5,
            condition="Cloudy",
            humidity=70,
            wind_speed=5.2,
            pressure=1013,
            fetched_at=datetime.now()
        )

        response = client.post("/subscribe/London", json={"email": "user@example.com"})
        assert response.status_code == 201

        data = response.json()
        assert data["success"] is True
        assert data["data"]["city"] == "London"
        assert data["data"]["email"] == "user@example.com"
        assert data["data"]["id"]
        assert data["error"] is None

    @patch('src.main.weather_client.get_weather')
    def test_subscribe_duplicate_409(self, mock_get_weather):
        """Повторная подписка на тот же город и email возвращает 409"""
        mock_get_weather.return_value = WeatherData(
            city="London",
            temp=15.5,
            condition="Cloudy",
            humidity=70,
            wind_speed=5.2,
            pressure=1013,
            fetched_at=datetime.now()
        )

        first_response = client.post("/subscribe/London", json={"email": "user@example.com"})
        second_response = client.post("/subscribe/London", json={"email": "user@example.com"})

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert "already exists" in second_response.json()["detail"].lower()
        assert mock_get_weather.call_count == 1

    def test_subscribe_invalid_email_422(self):
        """Некорректный email в запросе"""
        response = client.post("/subscribe/London", json={"email": "invalid-email"})
        assert response.status_code == 422

    @patch('src.main.weather_client.get_weather')
    def test_subscribe_city_not_found_400(self, mock_get_weather):
        """Подписка на несуществующий город"""
        mock_get_weather.side_effect = CityNotFound("City 'Atlantis' not found")

        response = client.post("/subscribe/Atlantis", json={"email": "user@example.com"})
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()


class TestGetSubscriptionsEndpoint:
    """Тесты GET /subscriptions"""
    
    def test_get_subscriptions_empty_list(self):
        """Получение пустого списка подписок"""
        response = client.get("/subscriptions")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] == []
        assert data["error"] is None
    
    @patch('src.main.weather_client.get_weather')
    def test_get_subscriptions_with_data(self, mock_get_weather):
        """Получение списка с подписками"""
        mock_get_weather.return_value = WeatherData(
            city="London",
            temp=15.5,
            condition="Cloudy",
            humidity=70,
            wind_speed=5.2,
            pressure=1013,
            fetched_at=datetime.now()
        )
        
        # Создаём подписки
        client.post("/subscribe/London", json={"email": "user1@example.com"})
        client.post("/subscribe/Paris", json={"email": "user2@example.com"})
        
        # Получаем список
        response = client.get("/subscriptions")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["error"] is None
    
    @patch('src.main.weather_client.get_weather')
    def test_get_subscriptions_after_delete(self, mock_get_weather):
        """Список обновляется после удаления"""
        mock_get_weather.return_value = WeatherData(
            city="London",
            temp=15.5,
            condition="Cloudy",
            humidity=70,
            wind_speed=5.2,
            pressure=1013,
            fetched_at=datetime.now()
        )
        
        # Создаём подписку
        sub_response = client.post("/subscribe/London", json={"email": "user@example.com"})
        sub_id = sub_response.json()["data"]["id"]
        
        # Проверяем, что она в списке
        response = client.get("/subscriptions")
        assert len(response.json()["data"]) == 1
        
        # Удаляем подписку
        client.delete(f"/subscribe/{sub_id}")
        
        # Проверяем, что список пуст
        response = client.get("/subscriptions")
        assert len(response.json()["data"]) == 0
    
    @patch('src.main.weather_client.get_weather')
    def test_get_subscriptions_returns_all_fields(self, mock_get_weather):
        """Проверка, что возвращаются все поля подписки"""
        mock_get_weather.return_value = WeatherData(
            city="London",
            temp=15.5,
            condition="Cloudy",
            humidity=70,
            wind_speed=5.2,
            pressure=1013,
            fetched_at=datetime.now()
        )
        
        # Создаём подписку
        client.post("/subscribe/London", json={"email": "user@example.com"})
        
        # Получаем список
        response = client.get("/subscriptions")
        data = response.json()
        subscription = data["data"][0]
        
        # Проверяем все поля
        assert "id" in subscription
        assert subscription["city"] == "London"
        assert subscription["email"] == "user@example.com"
        assert "created_at" in subscription


class TestWeatherClientIntegration:
    """Интеграционные тесты"""
    
    @patch('src.weather_client.httpx.Client')
    def test_weather_client_success(self, mock_client_class):
        """Успешный запрос к API"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {"temp": 15.5, "humidity": 70, "pressure": 1013},
            "weather": [{"main": "Cloudy"}],
            "wind": {"speed": 5.2}
        }
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response
        
        from src.weather_client import WeatherClient
        client_instance = WeatherClient(api_key="test_key")
        result = client_instance.get_weather("London")
        
        assert result.city == "London"
        assert result.temp == 15.5
        assert result.humidity == 70
        mock_client.get.assert_called_once_with(
            client_instance.base_url,
            params={
                "q": "London",
                "appid": "test_key",
                "units": "metric",
            },
        )
    
    @patch('src.weather_client.httpx.Client')
    def test_weather_client_city_not_found(self, mock_client_class):
        """Город не найден в API"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response
        
        from src.weather_client import WeatherClient
        client_instance = WeatherClient(api_key="test_key")
        
        with pytest.raises(CityNotFound):
            client_instance.get_weather("InvalidCity")
        mock_client.get.assert_called_once_with(
            client_instance.base_url,
            params={
                "q": "InvalidCity",
                "appid": "test_key",
                "units": "metric",
            },
        )
    
    @patch('src.weather_client.httpx.Client')
    def test_weather_client_api_error(self, mock_client_class):
        """Ошибка API"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response
        
        from src.weather_client import WeatherClient
        client_instance = WeatherClient(api_key="test_key")
        
        with pytest.raises(WeatherProviderError):
            client_instance.get_weather("London")
        mock_client.get.assert_called_once_with(
            client_instance.base_url,
            params={
                "q": "London",
                "appid": "test_key",
                "units": "metric",
            },
        )
