# Руководство по миграции на PostgreSQL

## 📋 Обзор

Этот документ описывает миграцию приложения WeatherApp с in-memory storage на PostgreSQL с использованием SQLAlchemy и Alembic.

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск PostgreSQL контейнера

```bash
docker-compose up -d
```

Проверка статуса:
```bash
docker-compose ps
```

### 3. Применение миграций

```bash
cd practices/practice_03
alembic upgrade head
```

### 4. Запуск приложения

```bash
cd practices/practice_03
uvicorn src.main:app --reload
```

Приложение будет доступно по адресу: `http://localhost:8000`

## 📁 Структура проекта

```
practices/practice_03/
├── src/
│   ├── main.py              # FastAPI приложение (обновлено)
│   ├── models.py            # Pydantic модели
│   ├── database.py          # Конфигурация БД (новое)
│   ├── db_models.py         # SQLAlchemy модели (новое)
│   ├── repository.py        # Repository pattern (новое)
│   └── weather_client.py    # Клиент погоды
├── tests/
│   └── test_weather_endpoint.py  # Тесты (обновлено)
├── alembic/                 # Миграции (новое)
│   ├── versions/
│   │   └── 001_create_subscriptions_table.py
│   ├── env.py
│   ├── script.py.mako
│   └── __init__.py
├── alembic.ini              # Конфигурация Alembic (новое)
└── MIGRATION_GUIDE.md       # Этот файл
```

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
DATABASE_URL=postgresql://weather_user:weather_password@localhost:5432/weather_db
OPENWEATHER_API_KEY=your_api_key_here
```

### Docker Compose

PostgreSQL запускается с параметрами:
- **User**: weather_user
- **Password**: weather_password
- **Database**: weather_db
- **Port**: 5432

## 📊 Архитектура

### Database Layer (`database.py`)

Содержит:
- Конфигурацию подключения к PostgreSQL
- Создание SQLAlchemy engine
- SessionLocal для работы с БД
- Функцию `get_db()` для dependency injection

### ORM Models (`db_models.py`)

Модель `Subscription`:
- `id`: UUID первичный ключ
- `email`: Email подписчика (индекс)
- `city`: Город для подписки (индекс)
- `created_at`: Время создания
- `updated_at`: Время последнего обновления
- Уникальное ограничение на (email, city)

### Repository Pattern (`repository.py`)

Класс `SubscriptionRepository` с методами:
- `create(email, city)` - создать подписку
- `get_by_id(subscription_id)` - получить по ID
- `get_all()` - получить все подписки
- `delete(subscription_id)` - удалить подписку
- `get_by_email_and_city(email, city)` - получить по email и городу

### API Layer (`main.py`)

Endpoints остаются теми же:
- `GET /health` - проверка здоровья
- `GET /weather/{city}` - получить погоду
- `POST /subribe/{city}` - создать подписку
- `DELETE /subscribe/{id}` - удалить подписку
- `GET /subscriptions` - получить все подписки

## 🗄️ Миграции Alembic

### Текущие миграции

**001_create_subscriptions_table.py** - создание таблицы subscriptions

### Применение миграций

```bash
# Применить все миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Просмотр текущей версии
alembic current

# История миграций
alembic history
```

### Создание новой миграции

```bash
# Автогенерация миграции
alembic revision --autogenerate -m "описание_изменения"

# Ручное создание миграции
alembic revision -m "описание_изменения"
```

## 🧪 Тестирование

### Запуск тестов

```bash
pytest practices/practice_03/tests/test_weather_endpoint.py -v
```

### Тестовая БД

Тесты используют SQLite в памяти для быстрого выполнения:
- Автоматическое создание таблиц перед каждым тестом
- Автоматическая очистка после каждого теста
- Не требует запущенного PostgreSQL

## 🔍 Проверка endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Получить погоду

```bash
curl http://localhost:8000/weather/London
```

### Создать подписку

```bash
curl -X POST http://localhost:8000/subribe/London \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### Получить все подписки

```bash
curl http://localhost:8000/subscriptions
```

### Удалить подписку

```bash
curl -X DELETE http://localhost:8000/subscribe/{subscription_id}
```

## 📝 Логирование

Приложение логирует все операции с подписками:

```
2026-03-19 18:45:00 - src.main - INFO - POST /subribe/London
2026-03-19 18:45:01 - src.main - INFO - Subscription created: 550e8400-e29b-41d4-a716-446655440000
```

## ⚠️ Обработка ошибок

### Дублирование подписок

Если попытаться создать подписку с тем же email и городом:
- **Status Code**: 409 Conflict
- **Detail**: "Subscription already exists"

### Несуществующий город

Если город не найден в API погоды:
- **Status Code**: 400 Bad Request
- **Detail**: "City 'CityName' not found"

### Несуществующая подписка

Если попытаться удалить несуществующую подписку:
- **Status Code**: 404 Not Found
- **Detail**: "Subscription with id 'xxx' not found"

## 🔄 Откат на in-memory версию

Если нужно вернуться на in-memory версию:

```bash
# Остановить контейнер
docker-compose down

# Откатить миграции
alembic downgrade base

# Удалить volume с данными
docker-compose down -v

# Вернуться к старой версии (git)
git checkout HEAD~1
```

## 📚 Дополнительные ресурсы

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## ✅ Проверочный список

- [ ] Docker установлен и работает
- [ ] PostgreSQL контейнер запущен (`docker-compose up -d`)
- [ ] Миграции применены (`alembic upgrade head`)
- [ ] Приложение запущено (`uvicorn src.main:app --reload`)
- [ ] Health check работает (`curl http://localhost:8000/health`)
- [ ] Тесты проходят (`pytest tests/test_weather_endpoint.py -v`)
- [ ] Все endpoints работают

## 🐛 Решение проблем

### Ошибка подключения к БД

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Решение**: Убедитесь, что PostgreSQL контейнер запущен:
```bash
docker-compose ps
docker-compose logs postgres
```

### Ошибка миграции

```
alembic.util.exc.CommandError: Can't locate revision identified by 'head'
```

**Решение**: Убедитесь, что находитесь в папке `practices/practice_03`:
```bash
cd practices/practice_03
alembic upgrade head
```

### Ошибка импорта модулей

```
ModuleNotFoundError: No module named 'src'
```

**Решение**: Убедитесь, что находитесь в папке `practices/practice_03` при запуске:
```bash
cd practices/practice_03
uvicorn src.main:app --reload
```

## 📞 Контакты

Для вопросов и проблем обратитесь к преподавателю или создайте issue в репозитории.
