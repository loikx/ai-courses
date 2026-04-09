# Data Model: Weather History

## Entity: StoredHistoricalWeather

- **Purpose**: Persistent cache of daily historical weather data for a
  normalized city and calendar date.
- **Storage location**: `practices/practice_03/src/db_models.py` and new Alembic
  migration `practices/practice_03/alembic/versions/002_create_weather_history_table.py`

### Fields

| Field | Type | Required | Rules | Notes |
|------|------|----------|-------|-------|
| `id` | UUID | yes | generated on insert | primary key |
| `city` | string | yes | normalized with trimmed whitespace and consistent casing rules used by the service | indexed |
| `date` | date | yes | one row per city per calendar day | part of unique key |
| `temp` | float | yes | provider-derived daily value | |
| `condition` | string | yes | non-empty provider-derived summary | |
| `humidity` | integer | yes | provider-derived | |
| `wind_speed` | float | yes | provider-derived | |
| `pressure` | integer | yes | provider-derived | |
| `fetched_at` | datetime | yes | set when provider data was retrieved | used for observability |
| `created_at` | datetime | yes | server default timestamp | |
| `updated_at` | datetime | yes | updated when row changes | |

### Constraints

- Unique constraint on `(city, date)`
- Index on `city`
- Composite index on `(city, date)`

## Entity: WeatherHistoryQuery

- **Purpose**: Service-layer representation of the requested history range.

### Fields

| Field | Type | Required | Rules |
|------|------|----------|-------|
| `city` | string | yes | normalized before provider or repository access |
| `start_date` | date | yes | must be less than or equal to `end_date` |
| `end_date` | date | yes | must not be in the future relative to service UTC date |

### Validation Rules

- Range length must be between 1 and 30 calendar days inclusive
- Invalid ISO date input must fail before service execution
- Future dates must return validation error response

## Entity: WeatherHistoryRecord

- **Purpose**: One response item returned to the caller for a single day.

### Fields

| Field | Type | Required | Rules |
|------|------|----------|-------|
| `date` | date | yes | ascending order in final response |
| `city` | string | yes | normalized city name |
| `temp` | float | yes | |
| `condition` | string | yes | |
| `humidity` | integer | yes | |
| `wind_speed` | float | yes | |
| `pressure` | integer | yes | |
| `fetched_at` | datetime | yes | |
| `source` | enum | yes | `cache` or `provider` |

## Entity: WeatherHistoryResponse

- **Purpose**: Aggregated payload returned by the API or manual command.

### Fields

| Field | Type | Required | Rules |
|------|------|----------|-------|
| `city` | string | yes | normalized city name |
| `start_date` | date | yes | echoes validated query |
| `end_date` | date | yes | echoes validated query |
| `records` | list[`WeatherHistoryRecord`] | yes | sorted by ascending date |

## Relationships

- One `WeatherHistoryQuery` yields one `WeatherHistoryResponse`
- One `WeatherHistoryResponse` contains many `WeatherHistoryRecord`
- One `StoredHistoricalWeather` row maps to one `WeatherHistoryRecord`
  when served from cache

## State and Lifecycle

1. Request arrives with `city`, `start_date`, and `end_date`
2. Service normalizes the city and validates the date range
3. Repository loads all `StoredHistoricalWeather` rows for the range
4. Service computes missing dates
5. Provider client returns data for missing dates only
6. Repository persists newly fetched rows
7. Service emits `WeatherHistoryRecord` list with correct `source` labels

## Error-Relevant Conditions

- Unknown city from provider -> user-facing `400`
- Provider outage or transport failure -> user-facing `503`
- Invalid range or future date -> user-facing `422`
- Database or unexpected internal error -> user-facing `500`
