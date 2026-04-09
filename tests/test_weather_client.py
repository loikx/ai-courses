from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.weather_client import HistoryAccessError
from src.weather_client import WeatherClient
from src.weather_client import WeatherProviderError


def test_get_history_requests_hourly_history_endpoint() -> None:
    """History API должен вызываться по координатам с параметром type=hour."""
    geocoding_response = MagicMock()
    geocoding_response.status_code = 200
    geocoding_response.json.return_value = [{"lat": 55.75, "lon": 37.61}]

    history_response = MagicMock()
    history_response.status_code = 200
    history_response.json.return_value = {
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
    http_client.get.side_effect = [geocoding_response, history_response]
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

    geocoding_params = http_client.get.call_args_list[0].kwargs["params"]
    history_params = http_client.get.call_args_list[1].kwargs["params"]
    assert geocoding_params["q"] == "Moscow"
    assert history_params["lat"] == 55.75
    assert history_params["lon"] == 37.61
    assert history_params["type"] == "hour"
    assert "q" not in history_params


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


def test_get_weather_maps_malformed_payload_to_provider_error() -> None:
    """Malformed current-weather payloads are mapped to provider errors."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"main": {"temp": 1.0}}
    http_client = MagicMock()
    http_client.get.return_value = response
    client_context = MagicMock()
    client_context.__enter__.return_value = http_client
    client_context.__exit__.return_value = False

    with patch("src.weather_client.httpx.Client", return_value=client_context):
        client = WeatherClient(api_key="test-api-key")
        with pytest.raises(WeatherProviderError, match=r"Malformed weather data"):
            client.get_weather("Moscow")


def test_get_history_maps_subscription_rejection_to_access_error() -> None:
    """Subscription-gated history responses expose an actionable error."""
    geocoding_response = MagicMock()
    geocoding_response.status_code = 200
    geocoding_response.json.return_value = [{"lat": 55.75, "lon": 37.61}]

    history_response = MagicMock()
    history_response.status_code = 403
    history_response.text = "history subscription required"

    http_client = MagicMock()
    http_client.get.side_effect = [geocoding_response, history_response]
    client_context = MagicMock()
    client_context.__enter__.return_value = http_client
    client_context.__exit__.return_value = False

    with patch("src.weather_client.httpx.Client", return_value=client_context):
        client = WeatherClient(api_key="test-api-key")
        with pytest.raises(HistoryAccessError, match=r"subscription tier"):
            client.get_history(
                city="Moscow",
                start_date=date(2026, 3, 20),
                end_date=date(2026, 3, 20),
            )


def test_get_history_free_tier_precheck_skips_http() -> None:
    """Configured free tier blocks history requests before provider calls."""
    with patch("src.weather_client.httpx.Client") as http_client_class:
        client = WeatherClient(api_key="test-api-key", subscription_tier="free")
        with pytest.raises(HistoryAccessError, match=r"paid subscription tier"):
            client.get_history(
                city="Moscow",
                start_date=date(2026, 3, 20),
                end_date=date(2026, 3, 20),
            )

    assert http_client_class.called is False
