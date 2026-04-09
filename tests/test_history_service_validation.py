from datetime import date

import pytest

from src.history_repository import HistoryRepository
from src.history_service import HistoryService
from src.history_service import HistoryValidationError


class RecordingWeatherClient:
    """Тестовый клиент провайдера, который сохраняет вызовы history-метода."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, date, date]] = []

    def get_history(
        self,
        city: str,
        start_date: date,
        end_date: date,
    ) -> list[object]:
        self.calls.append((city, start_date, end_date))
        return []


def test_get_history_rejects_start_date_after_end_date(db_session) -> None:
    """Сервис отклоняет диапазон, если start_date позже end_date."""
    repository = HistoryRepository(db_session)
    provider = RecordingWeatherClient()
    service = HistoryService(repository=repository, weather_client=provider)

    with pytest.raises(
        HistoryValidationError,
        match=r"start_date|end_date|range",
    ):
        service.get_history(
            city="Moscow",
            start_date=date(2026, 3, 22),
            end_date=date(2026, 3, 20),
        )

    assert provider.calls == []


def test_get_history_rejects_future_end_date_without_provider_call(db_session) -> None:
    """Сервис не обращается к провайдеру, если конец диапазона находится в будущем."""
    repository = HistoryRepository(db_session)
    provider = RecordingWeatherClient()
    service = HistoryService(repository=repository, weather_client=provider)

    with pytest.raises(
        HistoryValidationError,
        match=r"future|end_date",
    ):
        service.get_history(
            city="Moscow",
            start_date=date(2026, 3, 20),
            end_date=date(2099, 1, 1),
        )

    assert provider.calls == []
