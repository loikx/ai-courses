from unittest.mock import patch

from src.weather_client import CityNotFound, WeatherProviderError


@patch("src.main.weather_client.get_history")
def test_get_weather_history_returns_422_for_invalid_range(
    mock_get_history,
    client,
) -> None:
    """Endpoint возвращает 422, если start_date позже end_date."""
    response = client.get(
        "/weather/Moscow/history",
        params={"start_date": "2026-03-22", "end_date": "2026-03-20"},
    )

    assert response.status_code == 422
    assert "start_date" in str(response.json()["detail"]).lower()
    mock_get_history.assert_not_called()


@patch("src.main.weather_client.get_history")
def test_get_weather_history_returns_422_for_future_date(
    mock_get_history,
    client,
) -> None:
    """Endpoint возвращает 422, если диапазон уходит в будущее."""
    response = client.get(
        "/weather/Moscow/history",
        params={"start_date": "2026-03-20", "end_date": "2099-01-01"},
    )

    assert response.status_code == 422
    assert "future" in str(response.json()["detail"]).lower()
    mock_get_history.assert_not_called()


@patch("src.main.weather_client.get_history")
def test_get_weather_history_maps_city_not_found_to_400(
    mock_get_history,
    client,
) -> None:
    """Endpoint маппит ошибку неизвестного города в 400."""
    mock_get_history.side_effect = CityNotFound("City 'Atlantis' not found")

    response = client.get(
        "/weather/Atlantis/history",
        params={"start_date": "2026-03-20", "end_date": "2026-03-21"},
    )

    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()


@patch("src.main.weather_client.get_history")
def test_get_weather_history_maps_provider_error_to_503(
    mock_get_history,
    client,
) -> None:
    """Endpoint маппит сбой внешнего провайдера в 503."""
    mock_get_history.side_effect = WeatherProviderError("Weather API timeout")

    response = client.get(
        "/weather/Moscow/history",
        params={"start_date": "2026-03-20", "end_date": "2026-03-21"},
    )

    assert response.status_code == 503
    assert "temporarily unavailable" in response.json()["detail"].lower()
