"""Alembic environment configuration.

Конфигурация окружения Alembic для управления миграциями PostgreSQL.
Поддерживает как offline, так и online режимы миграций.
"""

import os
from logging.config import fileConfig
from sys import path as sys_path

import sqlalchemy as sa
from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

# Добавляем путь к src для импорта моделей
sys_path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from db_models import Base
except ImportError as e:
    raise ImportError(
        f"Не удалось импортировать db_models: {e}\n"
        "Убедитесь, что файл src/db_models.py существует и содержит Base"
    ) from e

# Alembic Config object - предоставляет значения из [alembic] секции .ini файла
config = context.config

# Настройка логирования из конфигурационного файла
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata объект для поддержки autogenerate
# Содержит все ORM модели, определенные в db_models.py
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("sqlalchemy.url")
# ... etc.


def get_required_database_url() -> str:
    """Return DATABASE_URL or fail before Alembic connects."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable must be set before running "
            "Alembic migrations"
        )
    return database_url


def ensure_pgcrypto_extension(connection) -> None:
    """Provision pgcrypto for gen_random_uuid() on PostgreSQL connections."""
    if connection.dialect.name == "postgresql":
        connection.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме.

    Этот режим используется для генерации SQL скриптов без подключения к БД.
    Конфигурирует контекст только с URL, без создания Engine.
    
    Вызовы context.execute() выводят SQL в stdout.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_required_database_url()

    context.configure(
        url=configuration["sqlalchemy.url"],
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме.

    Этот режим используется для применения миграций к реальной БД.
    Создает Engine и связывает соединение с контекстом Alembic.
    
    Поддерживает:
    - Автоматическое обнаружение изменений моделей (autogenerate)
    - Корректную обработку транзакций
    - Использование NullPool для избежания проблем с соединениями
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_required_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        ensure_pgcrypto_extension(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Поддержка autogenerate для автоматического обнаружения изменений
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
