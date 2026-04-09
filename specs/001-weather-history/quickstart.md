# Quickstart: Weather History

## 1. Prepare environment

From repository root:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp practices/practice_03/.env.example practices/practice_03/.env
docker compose up -d postgres
```

## 2. Apply database migrations

```bash
cd practices/practice_03
alembic upgrade head
cd "$(git rev-parse --show-toplevel)"
```

## 3. Start the API

```bash
cd practices/practice_03
uvicorn src.main:app --reload
```

## 4. Call the new history endpoint

```bash
curl "http://127.0.0.1:8000/weather/Moscow/history?start_date=2026-03-20&end_date=2026-03-22"
```

Expected result:

- HTTP `200` for valid city and valid date range
- `records` array sorted by ascending date
- `source` field shows whether each record came from `cache` or `provider`

## 5. Run the manual history command

```bash
cd practices/practice_03
python -m src.history_cli "Moscow" --start-date 2026-03-20 --end-date 2026-03-22 --format json
```

## 6. Run focused automated tests

```bash
pytest practices/practice_03/tests/test_history_service.py
pytest practices/practice_03/tests/test_weather_history_endpoint.py
pytest practices/practice_03/tests/test_weather_endpoint.py -k history
```

## 7. Verify cache behavior manually

1. Call the endpoint once for a valid range and confirm the request succeeds.
2. Call the same range again.
3. Check application logs and confirm the second request reports cached rows and
   does not require a full refetch from the provider.
