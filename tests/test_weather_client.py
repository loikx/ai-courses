from datetime import date
from unittest.mock import MagicMock, patch

from src.weather_client import WeatherClient


def test_get_history_requests_hourly_history_endpoint() -> None:
    """History API должен вызываться с параметром type=hour."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "list": [
            {
                "dt": 1773964800,
                "main": {
                    "temp": 1.5,
                    "humidity": 88,
                    "pressure": 1000,
                },
                "wind": {"speed": 5.8},
                "weather": [{"main": "Snow"}],
            }
        ]
    }
    http_client = MagicMock()
    http_client.get.return_value = response
    client_context = MagicMock()
    client_context.__enter__.return_value = http_client
    client_context.__exit__.return_value = False

    with patch("src.weather_client.httpx.Client", return_value=client_context):
        client = WeatherClient(api_key="test-api-key")
        client.get_history(
            city="Moscow",
            start_date=date(2026, 3, 20),
            end_date=date(2026, 3, 20),
        )

    params = http_client.get.call_args.kwargs["params"]
    assert params["type"] == "hour"


def test_get_history_returns_mock_data_without_http_call() -> None:
    """Mock-режим должен возвращать локальные данные без обращения к httpx."""
    with patch("src.weather_client.httpx.Client") as http_client_class:
        client = WeatherClient(api_key="test-api-key", mock_history_enabled=True)
        records = client.get_history(
            city="Moscow",
            start_date=date(2026, 3, 20),
            end_date=date(2026, 3, 22),
        )

    assert http_client_class.called is False
    assert [record.date.isoformat() for record in records] == [
        "2026-03-20",
        "2026-03-21",
        "2026-03-22",
    ]
    assert all(record.city == "Moscow" for record in records)
    assert records[0].condition == "MockClear"
