# Руководство по Alembic и миграциям базы данных

## 📋 Обзор

Этот документ описывает настройку и использование Alembic для управления миграциями PostgreSQL в проекте WeatherApp.

## 🏗️ Архитектура Alembic

### Структура проекта

```
practices/practice_03/
├── alembic/                          # Директория миграций
│   ├── versions/                     # Файлы миграций
│   │   ├── __init__.py
│   │   └── 001_create_subscriptions_table.py
│   ├── __init__.py
│   ├── env.py                        # Конфигурация окружения Alembic
│   └── script.py.mako                # Шаблон для новых миграций
├── alembic.ini                       # Конфигурация Alembic
├── src/
│   ├── database.py                   # Конфигурация SQLAlchemy engine
│   ├── db_models.py                  # ORM модели (Base + Subscription)
│   └── ...
└── ALEMBIC_SETUP.md                  # Этот файл
```

### Ключевые компоненты

#### 1. **alembic.ini** - Конфигурация
- `script_location` - путь к директории миграций
- `sqlalchemy.url` - URL подключения к БД (переопределяется `DATABASE_URL`)
- Настройки логирования

#### 2. **env.py** - Окружение Alembic
- Импортирует `Base` из `db_models.py`
- Поддерживает offline и online режимы
- Настроен для autogenerate (сравнение типов и server defaults)
- Использует переменную окружения `DATABASE_URL`

#### 3. **db_models.py** - ORM модели
- Содержит `Base = declarative_base()`
- Определяет модель `Subscription` с полями:
  - `id` (UUID primary key)
  - `email` (String, indexed)
  - `city` (String, indexed)
  - `created_at` (DateTime)
  - `updated_at` (DateTime)
  - Unique constraint на (email, city)

#### 4. **database.py** - Конфигурация БД
- Создает SQLAlchemy engine
- Инициализирует SessionLocal
- Предоставляет `get_db()` для dependency injection

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

Проверка установки Alembic:
```bash
alembic --version
```

### 2. Запуск PostgreSQL

```bash
docker-compose up -d
```

Проверка статуса:
```bash
docker-compose ps
```

Проверка подключения:
```bash
psql -U weather_user -d weather_db -h localhost -c "SELECT 1"
```

### 3. Применение миграций

Перейти в директорию проекта:
```bash
cd practices/practice_03
```

Применить все миграции:
```bash
alembic upgrade head
```

Проверить статус:
```bash
alembic current
```

### 4. Запуск приложения

```bash
cd practices/practice_03
uvicorn src.main:app --reload
```

Приложение доступно по адресу: `http://localhost:8000`

## 📝 Команды Alembic

### Основные команды

#### Применение миграций
```bash
# Применить все миграции до последней версии
alembic upgrade head

# Применить конкретное количество миграций
alembic upgrade +2

# Применить до конкретной версии
alembic upgrade 001
```

#### Откат миграций
```bash
# Откатить на одну версию назад
alembic downgrade -1

# Откатить все миграции
alembic downgrade base

# Откатить до конкретной версии
alembic downgrade 001
```

#### Просмотр статуса
```bash
# Показать текущую версию
alembic current

# Показать историю миграций
alembic history

# Показать историю в обратном порядке
alembic history --rev-range base:head
```

#### Создание новых миграций

**Вариант 1: Автоматическое обнаружение (autogenerate)**
```bash
# Alembic автоматически обнаружит изменения в моделях
alembic revision --autogenerate -m "Описание изменения"
```

**Вариант 2: Пустая миграция (для ручного написания)**
```bash
# Создать пустую миграцию для ручного заполнения
alembic revision -m "Описание изменения"
```

### Примеры использования

#### Добавление нового поля к таблице
```bash
# 1. Обновить модель в db_models.py
# 2. Создать миграцию
alembic revision --autogenerate -m "Add phone field to subscriptions"

# 3. Проверить сгенерированный файл в alembic/versions/
# 4. Применить миграцию
alembic upgrade head
```

#### Создание новой таблицы
```bash
# 1. Добавить новую модель в db_models.py
# 2. Создать миграцию
alembic revision --autogenerate -m "Create notifications table"

# 3. Применить миграцию
alembic upgrade head
```

## 🔍 Проверка миграций

### Smoke-check скрипт

Запустить проверку корректности миграций:
```bash
cd practices/practice_03
python scripts/check_migrations.py
```

Скрипт проверяет:
- ✅ Подключение к БД
- ✅ Наличие таблицы subscriptions
- ✅ Корректность структуры таблицы
- ✅ Наличие индексов
- ✅ Наличие constraints

### Ручная проверка в psql

```bash
# Подключиться к БД
psql -U weather_user -d weather_db -h localhost

# Показать таблицы
\dt

# Показать структуру таблицы subscriptions
\d subscriptions

# Показать индексы
\di

# Показать constraints
\d subscriptions
```

### Проверка через Python

```python
from sqlalchemy import inspect
from src.database import engine

inspector = inspect(engine)

# Показать все таблицы
tables = inspector.get_table_names()
print(f"Таблицы: {tables}")

# Показать колонки таблицы subscriptions
columns = inspector.get_columns('subscriptions')
for col in columns:
    print(f"  {col['name']}: {col['type']}")

# Показать индексы
indexes = inspector.get_indexes('subscriptions')
for idx in indexes:
    print(f"  Индекс: {idx['name']} на {idx['column_names']}")
```

## 🛠️ Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Обязательно
DATABASE_URL=postgresql://weather_user:weather_password@localhost:5432/weather_db

# Опционально
OPENWEATHER_API_KEY=your_api_key_here
```

### Параметры подключения PostgreSQL

По умолчанию используются параметры из `docker-compose.yml`:
- **Host**: localhost
- **Port**: 5432
- **User**: weather_user
- **Password**: weather_password
- **Database**: weather_db

Для изменения параметров отредактируйте `docker-compose.yml` или установите `DATABASE_URL`.

## 📊 Структура миграции

### Пример миграции: 001_create_subscriptions_table.py

```python
"""create_subscriptions_table

Revision ID: 001
Revises: 
Create Date: 2026-03-19 18:42:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Идентификаторы версии
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Применить миграцию (создать таблицу)"""
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', 'city', name='uq_subscription_email_city')
    )
    
    # Создание индексов
    op.create_index('idx_subscriptions_email', 'subscriptions', ['email'])
    op.create_index('idx_subscriptions_city', 'subscriptions', ['city'])


def downgrade() -> None:
    """Откатить миграцию (удалить таблицу)"""
    op.drop_index('idx_subscriptions_city', table_name='subscriptions')
    op.drop_index('idx_subscriptions_email', table_name='subscriptions')
    op.drop_table('subscriptions')
```

### Структура функций

- **upgrade()** - применить изменения (CREATE, ALTER, ADD)
- **downgrade()** - откатить изменения (DROP, REMOVE)

## ⚠️ Типичные проблемы и решения

### Проблема: "ModuleNotFoundError: No module named 'db_models'"

**Решение:**
- Убедитесь, что находитесь в директории `practices/practice_03`
- Проверьте, что `src/db_models.py` существует
- Проверьте `alembic/env.py` - там должна быть строка:
  ```python
  sys_path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
  ```

### Проблема: "FATAL: database 'weather_db' does not exist"

**Решение:**
- Убедитесь, что PostgreSQL контейнер запущен: `docker-compose ps`
- Проверьте переменную `DATABASE_URL`
- Создайте БД вручную:
  ```bash
  docker-compose exec postgres psql -U weather_user -c "CREATE DATABASE weather_db;"
  ```

### Проблема: "relation 'subscriptions' already exists"

**Решение:**
- Миграция уже была применена
- Проверьте статус: `alembic current`
- Если нужно переприменить, откатите и примените заново:
  ```bash
  alembic downgrade base
  alembic upgrade head
  ```

### Проблема: "UNIQUE constraint failed"

**Решение:**
- Попытка добавить дублирующуюся подписку (email + city)
- Проверьте данные в таблице:
  ```sql
  SELECT email, city, COUNT(*) FROM subscriptions GROUP BY email, city HAVING COUNT(*) > 1;
  ```

## 🔐 Безопасность

### Лучшие практики

1. **Никогда не коммитьте .env файл**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Используйте переменные окружения для чувствительных данных**
   ```python
   DATABASE_URL = os.getenv("DATABASE_URL")
   ```

3. **Проверяйте миграции перед применением**
   ```bash
   alembic upgrade --sql head  # Показать SQL без применения
   ```

4. **Делайте резервные копии перед миграциями**
   ```bash
   docker-compose exec postgres pg_dump -U weather_user weather_db > backup.sql
   ```

## 📚 Дополнительные ресурсы

- [Официальная документация Alembic](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## ✅ Чеклист для новых разработчиков

- [ ] Установлены зависимости (`pip install -r requirements.txt`)
- [ ] PostgreSQL контейнер запущен (`docker-compose up -d`)
- [ ] Миграции применены (`alembic upgrade head`)
- [ ] Проверка миграций пройдена (`python scripts/check_migrations.py`)
- [ ] Приложение запускается без ошибок (`uvicorn src.main:app --reload`)
- [ ] Можно создавать подписки через API (`POST /subscriptions`)
- [ ] Можно получать подписки через API (`GET /subscriptions`)

## 🎯 Следующие шаги

1. **Добавить новые таблицы** (notifications, logs, etc.)
2. **Настроить CI/CD** для автоматического применения миграций
3. **Добавить тесты** для проверки миграций
4. **Документировать** все изменения схемы БД
