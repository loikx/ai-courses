from datetime import date, datetime
from unittest.mock import patch

from src.db_models import StoredHistoricalWeather
from src.history_models import HistoricalWeatherProviderRecord


@patch("src.main.weather_client.get_history")
def test_get_weather_history_returns_sorted_multi_day_payload(
    mock_get_history,
    client,
    db_session,
) -> None:
    """Endpoint возвращает 200 и историю по диапазону в порядке возрастания дат."""
    mock_get_history.return_value = [
        HistoricalWeatherProviderRecord(
            date=date(2026, 3, 22),
            city="Moscow",
            temp=4.9,
            condition="Clouds",
            humidity=77,
            wind_speed=4.3,
            pressure=1007,
            fetched_at=datetime(2026, 3, 22, 10, 0, 0),
        ),
        HistoricalWeatherProviderRecord(
            date=date(2026, 3, 20),
            city="Moscow",
            temp=1.5,
            condition="Snow",
            humidity=88,
            wind_speed=5.8,
            pressure=1000,
            fetched_at=datetime(2026, 3, 20, 10, 0, 0),
        ),
        HistoricalWeatherProviderRecord(
            date=date(2026, 3, 21),
            city="Moscow",
            temp=3.2,
            condition="Clear",
            humidity=71,
            wind_speed=3.2,
            pressure=1009,
            fetched_at=datetime(2026, 3, 21, 10, 0, 0),
        ),
    ]

    response = client.get(
        "/weather/Moscow/history",
        params={"start_date": "2026-03-20", "end_date": "2026-03-22"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["city"] == "Moscow"
    assert body["data"]["start_date"] == "2026-03-20"
    assert body["data"]["end_date"] == "2026-03-22"
    assert [record["date"] for record in body["data"]["records"]] == [
        "2026-03-20",
        "2026-03-21",
        "2026-03-22",
    ]
    assert [record["source"] for record in body["data"]["records"]] == [
        "provider",
        "provider",
        "provider",
    ]
    assert body["error"] is None
    mock_get_history.assert_called_once_with(
        "Moscow",
        date(2026, 3, 20),
        date(2026, 3, 22),
    )

    stored_records = db_session.query(StoredHistoricalWeather).order_by(
        StoredHistoricalWeather.date.asc()
    )
    assert stored_records.count() == 3


@patch("src.main.weather_client.get_history")
def test_get_weather_history_returns_single_day_payload(
    mock_get_history,
    client,
) -> None:
    """Endpoint возвращает массив из одной записи для однодневного диапазона."""
    mock_get_history.return_value = [
        HistoricalWeatherProviderRecord(
            date=date(2026, 3, 20),
            city="Kazan",
            temp=8.1,
            condition="Rain",
            humidity=83,
            wind_speed=5.0,
            pressure=1003,
            fetched_at=datetime(2026, 3, 20, 8, 15, 0),
        )
    ]

    response = client.get(
        "/weather/Kazan/history",
        params={"start_date": "2026-03-20", "end_date": "2026-03-20"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["city"] == "Kazan"
    assert len(body["data"]["records"]) == 1
    assert body["data"]["records"][0]["date"] == "2026-03-20"
    assert body["data"]["records"][0]["source"] == "provider"


def test_get_weather_history_supports_mock_mode_without_paid_provider(
    client,
    db_session,
) -> None:
    """Endpoint должен обслуживать history-запрос в mock-режиме без внешнего API."""
    with patch("src.main.weather_client.mock_history_enabled", True):
        response = client.get(
            "/weather/Moscow/history",
            params={"start_date": "2026-03-20", "end_date": "2026-03-22"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert [record["date"] for record in body["data"]["records"]] == [
        "2026-03-20",
        "2026-03-21",
        "2026-03-22",
    ]
    assert [record["condition"] for record in body["data"]["records"]] == [
        "MockClear",
        "MockClouds",
        "MockRain",
    ]

    stored_records = db_session.query(StoredHistoricalWeather).order_by(
        StoredHistoricalWeather.date.asc()
    )
    assert stored_records.count() == 3
