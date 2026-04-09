from datetime import date, datetime
from unittest.mock import patch

from src.db_models import StoredHistoricalWeather
from src.history_models import HistoricalWeatherProviderRecord


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


@patch("src.main.weather_client.get_history")
def test_get_weather_history_serves_cache_hit_without_provider_call(
    mock_get_history,
    client,
    db_session,
) -> None:
    """Endpoint возвращает cache-hit диапазон без повторного обращения к провайдеру."""
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

    response = client.get(
        "/weather/Moscow/history",
        params={"start_date": "2026-03-20", "end_date": "2026-03-21"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert [record["source"] for record in body["data"]["records"]] == [
        "cache",
        "cache",
    ]
    mock_get_history.assert_not_called()


@patch("src.main.weather_client.get_history")
def test_get_weather_history_fetches_only_missing_days_for_partial_cache(
    mock_get_history,
    client,
    db_session,
) -> None:
    """Endpoint дозапрашивает у провайдера только отсутствующие даты и сохраняет их."""
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

    mock_get_history.return_value = [
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
    assert [record["source"] for record in body["data"]["records"]] == [
        "cache",
        "provider",
        "provider",
    ]
    mock_get_history.assert_called_once_with(
        "Moscow",
        date(2026, 3, 21),
        date(2026, 3, 22),
    )

    db_session.expire_all()
    stored_records = db_session.query(StoredHistoricalWeather).order_by(
        StoredHistoricalWeather.date.asc()
    )
    assert stored_records.count() == 3
