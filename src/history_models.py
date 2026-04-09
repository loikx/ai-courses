from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, field_validator


class HistoryRecordSource(str, Enum):
    CACHE = "cache"
    PROVIDER = "provider"


class WeatherHistoryQuery(BaseModel):
    city: str
    start_date: date
    end_date: date

    @field_validator("city")
    @classmethod
    def normalize_city(cls, value: str) -> str:
        return value.strip()


class HistoricalWeatherProviderRecord(BaseModel):
    date: date
    city: str
    temp: float
    condition: str
    humidity: int
    wind_speed: float
    pressure: int
    fetched_at: datetime


class WeatherHistoryRecord(BaseModel):
    date: date
    city: str
    temp: float
    condition: str
    humidity: int
    wind_speed: float
    pressure: int
    fetched_at: datetime
    source: HistoryRecordSource


class WeatherHistoryResponseData(BaseModel):
    city: str
    start_date: date
    end_date: date
    records: list[WeatherHistoryRecord]

    @field_validator("records")
    @classmethod
    def sort_records_by_date(
        cls,
        records: list[WeatherHistoryRecord],
    ) -> list[WeatherHistoryRecord]:
        return sorted(records, key=lambda record: record.date)


class WeatherHistoryResponse(BaseModel):
    success: bool
    data: WeatherHistoryResponseData | None = None
    error: str | None = None
