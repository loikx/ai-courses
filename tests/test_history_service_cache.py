from datetime import date, datetime

from src.db_models import StoredHistoricalWeather
from src.history_models import HistoricalWeatherProviderRecord, HistoryRecordSource
from src.history_repository import HistoryRepository
from src.history_service import HistoryService


class RecordingWeatherClient:
    """Тестовый клиент провайдера с фиксацией вызовов для cache-сценариев."""

    def __init__(self, records: list[HistoricalWeatherProviderRecord]) -> None:
        self.records = records
        self.calls: list[tuple[str, date, date]] = []

    def get_history(
        self,
        city: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalWeatherProviderRecord]:
        self.calls.append((city, start_date, end_date))
        return list(self.records)


def build_cached_row(
    *,
    city: str,
    row_date: date,
    temp: float,
    condition: str,
    humidity: int,
    wind_speed: float,
    pressure: int,
    fetched_at: datetime,
) -> StoredHistoricalWeather:
    return StoredHistoricalWeather(
        city=city,
        date=row_date,
        temp=temp,
        condition=condition,
        humidity=humidity,
        wind_speed=wind_speed,
        pressure=pressure,
        fetched_at=fetched_at,
    )


def test_get_history_uses_cache_without_provider_refetch(db_session) -> None:
    """Сервис отдаёт полностью закэшированный диапазон без повторного fetch к провайдеру."""
    db_session.add_all(
        [
            build_cached_row(
                city="Moscow",
                row_date=date(2026, 3, 20),
                temp=1.0,
                condition="Snow",
                humidity=82,
                wind_speed=5.1,
                pressure=1001,
                fetched_at=datetime(2026, 3, 20, 9, 0, 0),
            ),
            build_cached_row(
                city="Moscow",
                row_date=date(2026, 3, 21),
                temp=3.5,
                condition="Clear",
                humidity=70,
                wind_speed=3.0,
                pressure=1008,
                fetched_at=datetime(2026, 3, 21, 9, 0, 0),
            ),
        ]
    )
    db_session.commit()

    repository = HistoryRepository(db_session)
    provider = RecordingWeatherClient(records=[])
    service = HistoryService(repository=repository, weather_client=provider)

    response = service.get_history(
        city="Moscow",
        start_date=date(2026, 3, 20),
        end_date=date(2026, 3, 21),
    )

    assert provider.calls == []
    assert [record.date for record in response.records] == [
        date(2026, 3, 20),
        date(2026, 3, 21),
    ]
    assert [record.source for record in response.records] == [
        HistoryRecordSource.CACHE,
        HistoryRecordSource.CACHE,
    ]


def test_get_history_fetches_only_missing_days_for_partial_cache(db_session) -> None:
    """Сервис дозапрашивает у провайдера только отсутствующую часть диапазона."""
    db_session.add(
        build_cached_row(
            city="Moscow",
            row_date=date(2026, 3, 20),
            temp=1.0,
            condition="Snow",
            humidity=82,
            wind_speed=5.1,
            pressure=1001,
            fetched_at=datetime(2026, 3, 20, 9, 0, 0),
        )
    )
    db_session.commit()

    repository = HistoryRepository(db_session)
    provider = RecordingWeatherClient(
        [
            HistoricalWeatherProviderRecord(
                date=date(2026, 3, 21),
                city="Moscow",
                temp=3.5,
                condition="Clear",
                humidity=70,
                wind_speed=3.0,
                pressure=1008,
                fetched_at=datetime(2026, 3, 21, 9, 0, 0),
            ),
            HistoricalWeatherProviderRecord(
                date=date(2026, 3, 22),
                city="Moscow",
                temp=4.8,
                condition="Clouds",
                humidity=74,
                wind_speed=4.2,
                pressure=1006,
                fetched_at=datetime(2026, 3, 22, 9, 0, 0),
            ),
        ]
    )
    service = HistoryService(repository=repository, weather_client=provider)

    response = service.get_history(
        city="Moscow",
        start_date=date(2026, 3, 20),
        end_date=date(2026, 3, 22),
    )

    assert provider.calls == [("Moscow", date(2026, 3, 21), date(2026, 3, 22))]
    assert [record.date for record in response.records] == [
        date(2026, 3, 20),
        date(2026, 3, 21),
        date(2026, 3, 22),
    ]
    assert [record.source for record in response.records] == [
        HistoryRecordSource.CACHE,
        HistoryRecordSource.PROVIDER,
        HistoryRecordSource.PROVIDER,
    ]

    stored_records = repository.get_range(
        city="Moscow",
        start_date=date(2026, 3, 20),
        end_date=date(2026, 3, 22),
    )
    assert [record.date for record in stored_records] == [
        date(2026, 3, 20),
        date(2026, 3, 21),
        date(2026, 3, 22),
    ]
