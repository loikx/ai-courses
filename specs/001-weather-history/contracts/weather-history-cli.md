# Weather History Manual Command Contract

## Purpose

Define the manual invocation interface required for the history feature while
keeping it inside the existing Python project structure.

## Command Shape

```bash
python -m src.history_cli "<city>" --start-date YYYY-MM-DD --end-date YYYY-MM-DD --format <text|json>
```

## Inputs

| Argument | Required | Description |
|----------|----------|-------------|
| `city` | yes | City name passed in the same normalized form used by the API |
| `--start-date` | yes | Start date in `YYYY-MM-DD` format |
| `--end-date` | yes | End date in `YYYY-MM-DD` format |
| `--format` | no | Output format, defaults to `text`, allowed values: `text`, `json` |

## Successful Output

- `text`: human-readable summary containing city, range, and one line per day
- `json`: machine-readable payload matching the logical structure of the API
  success response

## Error Behavior

- Invalid dates or invalid range -> non-zero exit code and clear validation
  message on stderr
- Provider error -> non-zero exit code and provider-unavailable message
- City not found -> non-zero exit code and city-not-found message

## Compatibility Notes

- The command delegates to the same history service used by the FastAPI
  endpoint.
- Output fields must remain aligned with `WeatherHistoryRecord` and
  `WeatherHistoryResponse`.
