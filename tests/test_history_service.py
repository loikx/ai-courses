from datetime import date, datetime

from src.history_repository import HistoryRepository
from src.history_service import HistoryService
from src.history_models import HistoricalWeatherProviderRecord, HistoryRecordSource


class StubWeatherClient:
    """Тестовый клиент провайдера для детерминированных history-сценариев."""

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


def test_get_history_builds_sorted_response_and_persists_records(db_session) -> None:
    """Сервис собирает отсортированный диапазон и сохраняет данные провайдера."""
    repository = HistoryRepository(db_session)
    provider = StubWeatherClient(
        [
            HistoricalWeatherProviderRecord(
                date=date(2026, 3, 22),
                city="Moscow",
                temp=5.0,
                condition="Clouds",
                humidity=80,
                wind_speed=4.1,
                pressure=1005,
                fetched_at=datetime(2026, 3, 22, 9, 0, 0),
            ),
            HistoricalWeatherProviderRecord(
                date=date(2026, 3, 20),
                city="Moscow",
                temp=1.2,
                condition="Snow",
                humidity=84,
                wind_speed=5.0,
                pressure=1001,
                fetched_at=datetime(2026, 3, 20, 9, 0, 0),
            ),
            HistoricalWeatherProviderRecord(
                date=date(2026, 3, 21),
                city="Moscow",
                temp=3.6,
                condition="Clear",
                humidity=72,
                wind_speed=3.4,
                pressure=1008,
                fetched_at=datetime(2026, 3, 21, 9, 0, 0),
            ),
        ]
    )
    service = HistoryService(repository=repository, weather_client=provider)

    response = service.get_history(
        city="  Moscow  ",
        start_date=date(2026, 3, 20),
        end_date=date(2026, 3, 22),
    )

    assert response.city == "Moscow"
    assert response.start_date == date(2026, 3, 20)
    assert response.end_date == date(2026, 3, 22)
    assert [record.date for record in response.records] == [
        date(2026, 3, 20),
        date(2026, 3, 21),
        date(2026, 3, 22),
    ]
    assert [record.source for record in response.records] == [
        HistoryRecordSource.PROVIDER,
        HistoryRecordSource.PROVIDER,
        HistoryRecordSource.PROVIDER,
    ]
    assert provider.calls == [("Moscow", date(2026, 3, 20), date(2026, 3, 22))]

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


def test_get_history_returns_single_record_for_single_day_range(db_session) -> None:
    """Сервис возвращает массив из одной записи, если диапазон состоит из одного дня."""
    repository = HistoryRepository(db_session)
    provider = StubWeatherClient(
        [
            HistoricalWeatherProviderRecord(
                date=date(2026, 3, 20),
                city="Saint Petersburg",
                temp=7.4,
                condition="Rain",
                humidity=86,
                wind_speed=6.2,
                pressure=998,
                fetched_at=datetime(2026, 3, 20, 7, 30, 0),
            )
        ]
    )
    service = HistoryService(repository=repository, weather_client=provider)

    response = service.get_history(
        city="Saint Petersburg",
        start_date=date(2026, 3, 20),
        end_date=date(2026, 3, 20),
    )

    assert response.city == "Saint Petersburg"
    assert len(response.records) == 1
    assert response.records[0].date == date(2026, 3, 20)
    assert response.records[0].source == HistoryRecordSource.PROVIDER
