#!/usr/bin/env python3
"""
Скрипт инициализации миграций для проекта WeatherApp.

Выполняет:
1. Проверку подключения к БД
2. Применение всех миграций
3. Проверку корректности миграций
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text: str) -> None:
    """Вывести заголовок."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def run_command(cmd: list, description: str) -> bool:
    """Запустить команду и вывести результат."""
    print(f"▶️  {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ {description} - успешно")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ошибка")
        print(f"   Команда: {' '.join(cmd)}")
        if e.stderr:
            print(f"   Ошибка: {e.stderr}")
        return False


def main():
    """Главная функция."""
    print_header("Инициализация миграций WeatherApp")
    
    # Получить путь к директории проекта
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    
    print(f"📁 Рабочая директория: {project_dir}\n")
    
    # Проверить наличие alembic.ini
    if not (project_dir / "alembic.ini").exists():
        print("❌ Ошибка: alembic.ini не найден")
        print(f"   Ожидается в: {project_dir / 'alembic.ini'}")
        return False
    
    # Проверить наличие alembic/env.py
    if not (project_dir / "alembic" / "env.py").exists():
        print("❌ Ошибка: alembic/env.py не найден")
        print(f"   Ожидается в: {project_dir / 'alembic' / 'env.py'}")
        return False
    
    # Проверить наличие src/db_models.py
    if not (project_dir / "src" / "db_models.py").exists():
        print("❌ Ошибка: src/db_models.py не найден")
        print(f"   Ожидается в: {project_dir / 'src' / 'db_models.py'}")
        return False
    
    print("✅ Все необходимые файлы найдены\n")
    
    # Применить миграции
    print_header("Применение миграций")
    
    if not run_command(
        ["alembic", "upgrade", "head"],
        "Применение миграций (alembic upgrade head)"
    ):
        print("\n⚠️  Миграции не были применены")
        print("   Проверьте подключение к БД и переменную DATABASE_URL")
        return False
    
    # Проверить текущую версию
    print_header("Проверка статуса миграций")
    
    if not run_command(
        ["alembic", "current"],
        "Проверка текущей версии (alembic current)"
    ):
        print("\n⚠️  Не удалось получить текущую версию")
        return False
    
    # Показать историю миграций
    print_header("История миграций")
    
    if not run_command(
        ["alembic", "history"],
        "Показать историю миграций (alembic history)"
    ):
        print("\n⚠️  Не удалось получить историю миграций")
        return False
    
    # Запустить smoke-check
    print_header("Проверка корректности миграций")
    
    check_script = project_dir / "scripts" / "check_migrations.py"
    if check_script.exists():
        if not run_command(
            ["python", str(check_script)],
            "Запуск smoke-check (scripts/check_migrations.py)"
        ):
            print("\n⚠️  Smoke-check выявил проблемы")
            return False
    else:
        print(f"⚠️  Smoke-check скрипт не найден: {check_script}")
    
    # Итоги
    print_header("✅ Инициализация завершена успешно")
    
    print("Следующие шаги:")
    print("1. Запустить приложение:")
    print("   uvicorn src.main:app --reload")
    print("\n2. Проверить API:")
    print("   curl http://localhost:8000/docs")
    print("\n3. Создать подписку:")
    print("   curl -X POST http://localhost:8000/subscriptions \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"email\": \"user@example.com\", \"city\": \"Moscow\"}'")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
