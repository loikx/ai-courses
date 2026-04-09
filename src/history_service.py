import logging
from datetime import date, datetime, timedelta, timezone

from .history_models import (
    HistoricalWeatherProviderRecord,
    HistoryRecordSource,
    WeatherHistoryQuery,
    WeatherHistoryRecord,
    WeatherHistoryResponseData,
)
from .history_repository import HistoryRepository
from .weather_client import WeatherClient


logger = logging.getLogger(__name__)


class HistoryValidationError(ValueError):
    """Ошибка пользовательского диапазона истории погоды."""


class HistoryService:
    """Собирает историю погоды из провайдера и локального хранилища."""

    def __init__(
        self,
        repository: HistoryRepository,
        weather_client: WeatherClient,
    ) -> None:
        self.repository = repository
        self.weather_client = weather_client

    def get_history(
        self,
        city: str,
        start_date: date,
        end_date: date,
    ) -> WeatherHistoryResponseData:
        query = WeatherHistoryQuery(
            city=city,
            start_date=start_date,
            end_date=end_date,
        )
        self._validate_query(query)

        cached_rows = self.repository.get_range(
            city=query.city,
            start_date=query.start_date,
            end_date=query.end_date,
        )
        cached_dates = {row.date for row in cached_rows}
        expected_dates = self._date_range(query.start_date, query.end_date)
        missing_dates = [
            current_date for current_date in expected_dates
            if current_date not in cached_dates
        ]

        provider_records: list[HistoricalWeatherProviderRecord] = []
        if missing_dates:
            provider_records = self.weather_client.get_history(
                query.city,
                min(missing_dates),
                max(missing_dates),
            )
            self.repository.upsert_many(query.city, provider_records)

        response = WeatherHistoryResponseData(
            city=query.city,
            start_date=query.start_date,
            end_date=query.end_date,
            records=self._assemble_records(
                city=query.city,
                cached_rows=cached_rows,
                provider_records=provider_records,
            ),
        )
        logger.info(
            "History request assembled city=%s start_date=%s end_date=%s cache_rows=%s provider_rows=%s returned_rows=%s",
            query.city,
            query.start_date,
            query.end_date,
            len(cached_rows),
            len(provider_records),
            len(response.records),
        )
        return response

    @staticmethod
    def _validate_query(query: WeatherHistoryQuery) -> None:
        if query.start_date > query.end_date:
            raise HistoryValidationError("start_date must be before or equal to end_date")

        today_utc = datetime.now(timezone.utc).date()
        if query.end_date > today_utc:
            raise HistoryValidationError("end_date must not be in the future")

        range_days = (query.end_date - query.start_date).days + 1
        if range_days > 30:
            raise HistoryValidationError("date range must not exceed 30 days")

    @staticmethod
    def _date_range(start_date: date, end_date: date) -> list[date]:
        days_count = (end_date - start_date).days + 1
        return [
            start_date + timedelta(days=offset)
            for offset in range(days_count)
        ]

    def _assemble_records(
        self,
        city: str,
        cached_rows: list[object],
        provider_records: list[HistoricalWeatherProviderRecord],
    ) -> list[WeatherHistoryRecord]:
        records_by_date: dict[date, WeatherHistoryRecord] = {}

        for row in cached_rows:
            records_by_date[row.date] = self._cached_row_to_history_record(row)

        for record in provider_records:
            records_by_date[record.date] = self._to_provider_history_record(city, record)

        return sorted(records_by_date.values(), key=lambda record: record.date)

    @staticmethod
    def _cached_row_to_history_record(row: object) -> WeatherHistoryRecord:
        return WeatherHistoryRecord(
            date=row.date,
            city=row.city,
            temp=row.temp,
            condition=row.condition,
            humidity=row.humidity,
            wind_speed=row.wind_speed,
            pressure=row.pressure,
            fetched_at=row.fetched_at,
            source=HistoryRecordSource.CACHE,
        )

    @staticmethod
    def _to_provider_history_record(
        city: str,
        record: HistoricalWeatherProviderRecord,
    ) -> WeatherHistoryRecord:
        return WeatherHistoryRecord(
            date=record.date,
            city=city,
            temp=record.temp,
            condition=record.condition,
            humidity=record.humidity,
            wind_speed=record.wind_speed,
            pressure=record.pressure,
            fetched_at=record.fetched_at,
            source=HistoryRecordSource.PROVIDER,
        )
