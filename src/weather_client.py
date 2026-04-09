import httpx
import logging
from datetime import date, datetime, time, timedelta, timezone

from .history_models import HistoricalWeatherProviderRecord
from .models import WeatherData

logger = logging.getLogger(__name__)


class CityNotFound(Exception):
    """Город не найден"""
    pass


class WeatherProviderError(Exception):
    """Ошибка API погоды"""
    pass


class WeatherClient:
    """Клиент для OpenWeatherMap API"""
    
    def __init__(self, api_key: str, mock_history_enabled: bool = False):
        self.api_key = api_key
        self.mock_history_enabled = mock_history_enabled
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.history_base_url = "https://history.openweathermap.org/data/2.5/history/city"
    
    def get_weather(self, city: str) -> WeatherData:
        """Получить погоду для города"""
        logger.info(f"Fetching weather for {city}")
        
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.base_url, params=params)
                
                if response.status_code == 404:
                    logger.error(f"City not found: {city}")
                    raise CityNotFound(f"City '{city}' not found")
                
                if response.status_code >= 500:
                    logger.error(f"API error: {response.status_code}")
                    raise WeatherProviderError(f"Weather API error: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"API error: {response.status_code}")
                    raise WeatherProviderError(f"Weather API error: {response.status_code}")
                
                data = response.json()
                return self._parse_response(city, data)
        
        except httpx.TimeoutException:
            logger.error("API timeout")
            raise WeatherProviderError("Weather API timeout")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise WeatherProviderError(f"Request error: {str(e)}")
    
    def _parse_response(self, city: str, data: dict) -> WeatherData:
        """Парсить ответ API"""
        return WeatherData(
            city=city,
            temp=data["main"]["temp"],
            condition=data["weather"][0]["main"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"],
            pressure=data["main"]["pressure"],
            fetched_at=datetime.now()
        )

    def get_history(
        self,
        city: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalWeatherProviderRecord]:
        """Получить дневную историю погоды для диапазона дат."""
        logger.info("Fetching history for %s from %s to %s", city, start_date, end_date)

        if self.mock_history_enabled:
            logger.info(
                "Returning mock history for %s from %s to %s",
                city,
                start_date,
                end_date,
            )
            return self._build_mock_history(
                city=city,
                start_date=start_date,
                end_date=end_date,
            )

        start_timestamp = int(
            datetime.combine(
                start_date,
                time.min,
                tzinfo=timezone.utc,
            ).timestamp()
        )
        end_timestamp = int(
            datetime.combine(
                end_date,
                time.max,
                tzinfo=timezone.utc,
            ).timestamp()
        )
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "type": "hour",
            "start": start_timestamp,
            "end": end_timestamp,
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.history_base_url, params=params)

                if response.status_code == 404:
                    logger.error("City not found: %s", city)
                    raise CityNotFound(f"City '{city}' not found")

                if response.status_code >= 500:
                    logger.error("History API error: %s", response.status_code)
                    raise WeatherProviderError(
                        f"Weather API error: {response.status_code}"
                    )

                if response.status_code != 200:
                    logger.error("History API error: %s", response.status_code)
                    raise WeatherProviderError(
                        f"Weather API error: {response.status_code}"
                    )

                data = response.json()
                return self._parse_history_response(city, start_date, end_date, data)

        except httpx.TimeoutException:
            logger.error("History API timeout")
            raise WeatherProviderError("Weather API timeout")
        except httpx.RequestError as error:
            logger.error("History request error: %s", error)
            raise WeatherProviderError(f"Request error: {str(error)}")

    def _parse_history_response(
        self,
        city: str,
        start_date: date,
        end_date: date,
        data: dict,
    ) -> list[HistoricalWeatherProviderRecord]:
        """Парсить history-ответ API в дневные записи."""
        raw_records = data.get("list", [])
        if not raw_records:
            raise WeatherProviderError("Weather history data unavailable")

        records_by_date: dict[date, HistoricalWeatherProviderRecord] = {}
        for item in raw_records:
            observed_at = datetime.fromtimestamp(item["dt"], tz=timezone.utc).replace(
                tzinfo=None
            )
            observed_date = observed_at.date()
            if observed_date < start_date or observed_date > end_date:
                continue

            if observed_date in records_by_date:
                continue

            records_by_date[observed_date] = HistoricalWeatherProviderRecord(
                date=observed_date,
                city=city,
                temp=item["main"]["temp"],
                condition=item["weather"][0]["main"],
                humidity=item["main"]["humidity"],
                wind_speed=item["wind"]["speed"],
                pressure=item["main"]["pressure"],
                fetched_at=observed_at,
            )

        if not records_by_date:
            raise WeatherProviderError("Weather history data unavailable")

        return sorted(records_by_date.values(), key=lambda record: record.date)

    def _build_mock_history(
        self,
        city: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalWeatherProviderRecord]:
        """Сгенерировать детерминированные данные для локальной history-разработки."""
        records: list[HistoricalWeatherProviderRecord] = []
        conditions = ["MockClear", "MockClouds", "MockRain", "MockWind"]
        current_date = start_date
        day_index = 0

        while current_date <= end_date:
            records.append(
                HistoricalWeatherProviderRecord(
                    date=current_date,
                    city=city,
                    temp=10.0 + day_index,
                    condition=conditions[day_index % len(conditions)],
                    humidity=60 + day_index,
                    wind_speed=3.0 + (day_index * 0.5),
                    pressure=1000 + day_index,
                    fetched_at=datetime.combine(
                        current_date,
                        time(hour=12, minute=0),
                    ),
                )
            )
            current_date += timedelta(days=1)
            day_index += 1

        return records
