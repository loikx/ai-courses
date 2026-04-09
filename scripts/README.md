# Скрипты для управления миграциями

## 📋 Обзор

Директория `scripts/` содержит вспомогательные скрипты для управления миграциями базы данных.

## 🚀 Скрипты

### 1. init_migrations.py - Инициализация миграций

**Назначение:** Автоматическое применение всех миграций и проверка корректности.

**Использование:**
```bash
cd practices/practice_03
python scripts/init_migrations.py
```

**Что делает:**
1. ✅ Проверяет наличие необходимых файлов (alembic.ini, env.py, db_models.py)
2. ✅ Применяет все миграции (`alembic upgrade head`)
3. ✅ Проверяет текущую версию (`alembic current`)
4. ✅ Показывает историю миграций (`alembic history`)
5. ✅ Запускает smoke-check для проверки корректности

**Вывод:**
```
============================================================
  Инициализация миграций WeatherApp
============================================================

📁 Рабочая директория: /path/to/practices/practice_03

✅ Все необходимые файлы найдены

============================================================
  Применение миграций
============================================================

▶️  Применение миграций (alembic upgrade head)...
✅ Применение миграций (alembic upgrade head) - успешно

...

✅ Инициализация завершена успешно
```

### 2. check_migrations.py - Smoke-check миграций

**Назначение:** Проверка корректности структуры БД и работоспособности миграций.

**Использование:**
```bash
cd practices/practice_03
python scripts/check_migrations.py
```

**Что проверяет:**
1. ✅ Подключение к PostgreSQL
2. ✅ Наличие таблицы `subscriptions`
3. ✅ Структура таблицы (все колонки присутствуют)
4. ✅ Типы данных колонок
5. ✅ Наличие индексов (`idx_subscriptions_email`, `idx_subscriptions_city`)
6. ✅ Наличие constraints (primary key, unique constraint)
7. ✅ CRUD операции (CREATE, READ, UPDATE, DELETE)
8. ✅ Работа unique constraint

**Вывод:**
```
============================================================
  SMOKE-CHECK: Проверка миграций Alembic
============================================================

============================================================
  1. Проверка подключения к БД
============================================================

✅ PASS | Подключение к PostgreSQL

============================================================
  2. Проверка наличия таблицы
============================================================

✅ PASS | Таблица 'subscriptions' существует
       Найденные таблицы: ['subscriptions']

...

============================================================
  ИТОГИ
============================================================

✅ Пройдено: 12/12
❌ Ошибок: 0/12

🎉 Все проверки пройдены успешно!
```

## 🔧 Примеры использования

### Полная инициализация проекта

```bash
# 1. Перейти в директорию проекта
cd practices/practice_03

# 2. Установить зависимости
pip install -r ../../requirements.txt

# 3. Запустить PostgreSQL
docker-compose up -d

# 4. Инициализировать миграции
python scripts/init_migrations.py

# 5. Запустить приложение
uvicorn src.main:app --reload
```

### Проверка после изменения моделей

```bash
# 1. Обновить модель в src/db_models.py
# 2. Создать миграцию
alembic revision --autogenerate -m "Описание изменения"

# 3. Применить миграцию
alembic upgrade head

# 4. Проверить корректность
python scripts/check_migrations.py
```

### Откат миграций

```bash
# Откатить на одну версию назад
alembic downgrade -1

# Откатить все миграции
alembic downgrade base

# Проверить корректность
python scripts/check_migrations.py
```

## 📊 Структура скриптов

### init_migrations.py

```
main()
├── Проверка файлов
│   ├── alembic.ini
│   ├── alembic/env.py
│   └── src/db_models.py
├── Применение миграций
│   └── alembic upgrade head
├── Проверка статуса
│   ├── alembic current
│   └── alembic history
└── Smoke-check
    └── scripts/check_migrations.py
```

### check_migrations.py

```
MigrationChecker
├── check_database_connection()
├── check_table_exists()
├── check_table_structure()
├── check_indexes()
├── check_constraints()
├── check_crud_operations()
├── check_unique_constraint()
└── run_all_checks()
```

## ⚠️ Типичные проблемы

### Проблема: "ModuleNotFoundError: No module named 'src'"

**Решение:**
```bash
# Убедитесь, что находитесь в директории practices/practice_03
cd practices/practice_03
python scripts/check_migrations.py
```

### Проблема: "FATAL: database 'weather_db' does not exist"

**Решение:**
```bash
# Запустить PostgreSQL контейнер
docker-compose up -d

# Проверить статус
docker-compose ps

# Создать БД вручную (если нужно)
docker-compose exec postgres psql -U weather_user -c "CREATE DATABASE weather_db;"
```

### Проблема: "permission denied" при запуске скрипта

**Решение:**
```bash
# Дать права на выполнение
chmod +x scripts/init_migrations.py
chmod +x scripts/check_migrations.py

# Запустить скрипт
python scripts/init_migrations.py
```

## 🎯 Интеграция с CI/CD

### GitHub Actions

```yaml
name: Database Migrations

on: [push, pull_request]

jobs:
  migrations:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: weather_user
          POSTGRES_PASSWORD: weather_password
          POSTGRES_DB: weather_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run migrations
        working-directory: practices/practice_03
        run: python scripts/init_migrations.py
```

## 📚 Дополнительные ресурсы

- [ALEMBIC_SETUP.md](./ALEMBIC_SETUP.md) - Полное руководство по Alembic
- [Официальная документация Alembic](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)

## ✅ Чеклист

- [ ] Скрипты находятся в `practices/practice_03/scripts/`
- [ ] Скрипты имеют права на выполнение
- [ ] PostgreSQL контейнер запущен
- [ ] Переменная `DATABASE_URL` установлена (или используется значение по умолчанию)
- [ ] `init_migrations.py` выполняется без ошибок
- [ ] `check_migrations.py` выполняется без ошибок
- [ ] Все проверки в smoke-check пройдены
