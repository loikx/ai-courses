from datetime import date
from collections.abc import Sequence

from sqlalchemy.orm import Session

from .db_models import StoredHistoricalWeather
from .history_models import HistoricalWeatherProviderRecord


class HistoryRepository:
    """Repository для чтения и сохранения history-записей."""

    def __init__(self, db: Session):
        self.db = db

    def get_range(
        self,
        city: str,
        start_date: date,
        end_date: date,
    ) -> list[StoredHistoricalWeather]:
        return (
            self.db.query(StoredHistoricalWeather)
            .filter(
                StoredHistoricalWeather.city == city,
                StoredHistoricalWeather.date >= start_date,
                StoredHistoricalWeather.date <= end_date,
            )
            .order_by(StoredHistoricalWeather.date.asc())
            .all()
        )

    def upsert_many(
        self,
        city: str,
        records: Sequence[HistoricalWeatherProviderRecord],
    ) -> list[StoredHistoricalWeather]:
        if not records:
            return []

        dates = [record.date for record in records]
        existing_rows = (
            self.db.query(StoredHistoricalWeather)
            .filter(
                StoredHistoricalWeather.city == city,
                StoredHistoricalWeather.date.in_(dates),
            )
            .all()
        )
        existing_by_date = {row.date: row for row in existing_rows}
        persisted_rows: list[StoredHistoricalWeather] = []

        try:
            for record in records:
                row = existing_by_date.get(record.date)
                if row is None:
                    row = StoredHistoricalWeather(city=city, date=record.date)
                    self.db.add(row)

                row.city = city
                row.temp = record.temp
                row.condition = record.condition
                row.humidity = record.humidity
                row.wind_speed = record.wind_speed
                row.pressure = record.pressure
                row.fetched_at = record.fetched_at
                persisted_rows.append(row)

            self.db.commit()

            for row in persisted_rows:
                self.db.refresh(row)
        except Exception:
            self.db.rollback()
            raise

        return sorted(persisted_rows, key=lambda row: row.date)
