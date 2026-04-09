#!/usr/bin/env python3
"""
Smoke-check скрипт для проверки корректности миграций Alembic.

Проверяет:
- Подключение к БД
- Наличие таблицы subscriptions
- Корректность структуры таблицы
- Наличие индексов
- Наличие constraints
- Возможность выполнения базовых операций CRUD
"""

import os
import sys
from pathlib import Path

# Добавляем путь к src для импорта моделей
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from src.database import engine, SessionLocal
from src.db_models import Subscription, Base
from uuid import uuid4
from datetime import datetime


class MigrationChecker:
    """Класс для проверки корректности миграций."""

    def __init__(self):
        self.engine = engine
        self.session = SessionLocal()
        self.checks_passed = 0
        self.checks_failed = 0

    def print_header(self, text: str) -> None:
        """Вывести заголовок секции."""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}")

    def print_check(self, name: str, passed: bool, message: str = "") -> None:
        """Вывести результат проверки."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {name}")
        if message:
            print(f"       {message}")
        
        if passed:
            self.checks_passed += 1
        else:
            self.checks_failed += 1

    def check_database_connection(self) -> bool:
        """Проверить подключение к БД."""
        self.print_header("1. Проверка подключения к БД")
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            self.print_check("Подключение к PostgreSQL", True)
            return True
        except SQLAlchemyError as e:
            self.print_check("Подключение к PostgreSQL", False, str(e))
            return False

    def check_table_exists(self) -> bool:
        """Проверить наличие таблицы subscriptions."""
        self.print_header("2. Проверка наличия таблицы")
        
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            table_exists = 'subscriptions' in tables
            self.print_check(
                "Таблица 'subscriptions' существует",
                table_exists,
                f"Найденные таблицы: {tables}"
            )
            return table_exists
        except SQLAlchemyError as e:
            self.print_check("Таблица 'subscriptions' существует", False, str(e))
            return False

    def check_table_structure(self) -> bool:
        """Проверить структуру таблицы."""
        self.print_header("3. Проверка структуры таблицы")
        
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns('subscriptions')
            
            column_names = {col['name'] for col in columns}
            expected_columns = {'id', 'email', 'city', 'created_at', 'updated_at'}
            
            all_present = expected_columns.issubset(column_names)
            self.print_check(
                "Все необходимые колонки присутствуют",
                all_present,
                f"Колонки: {column_names}"
            )
            
            # Проверить типы колонок
            for col in columns:
                if col['name'] == 'email':
                    is_string = 'VARCHAR' in str(col['type']).upper() or 'STRING' in str(col['type']).upper()
                    self.print_check(
                        f"Колонка 'email' имеет тип String",
                        is_string,
                        f"Тип: {col['type']}"
                    )
                elif col['name'] == 'city':
                    is_string = 'VARCHAR' in str(col['type']).upper() or 'STRING' in str(col['type']).upper()
                    self.print_check(
                        f"Колонка 'city' имеет тип String",
                        is_string,
                        f"Тип: {col['type']}"
                    )
            
            return all_present
        except SQLAlchemyError as e:
            self.print_check("Структура таблицы корректна", False, str(e))
            return False

    def check_indexes(self) -> bool:
        """Проверить наличие индексов."""
        self.print_header("4. Проверка индексов")
        
        try:
            inspector = inspect(self.engine)
            indexes = inspector.get_indexes('subscriptions')
            
            index_names = {idx['name'] for idx in indexes}
            expected_indexes = {'idx_subscriptions_email', 'idx_subscriptions_city'}
            
            all_present = expected_indexes.issubset(index_names)
            self.print_check(
                "Все необходимые индексы присутствуют",
                all_present,
                f"Индексы: {index_names}"
            )
            
            return all_present
        except SQLAlchemyError as e:
            self.print_check("Индексы присутствуют", False, str(e))
            return False

    def check_constraints(self) -> bool:
        """Проверить наличие constraints."""
        self.print_header("5. Проверка constraints")
        
        try:
            inspector = inspect(self.engine)
            
            # Проверить primary key
            pk = inspector.get_pk_constraint('subscriptions')
            has_pk = pk and 'id' in pk.get('constrained_columns', [])
            self.print_check(
                "Primary key на колонке 'id' присутствует",
                has_pk,
                f"PK: {pk}"
            )
            
            # Проверить unique constraint
            constraints = inspector.get_unique_constraints('subscriptions')
            constraint_names = {c['name'] for c in constraints}
            has_unique = 'uq_subscription_email_city' in constraint_names
            self.print_check(
                "Unique constraint на (email, city) присутствует",
                has_unique,
                f"Constraints: {constraint_names}"
            )
            
            return has_pk and has_unique
        except SQLAlchemyError as e:
            self.print_check("Constraints присутствуют", False, str(e))
            return False

    def check_crud_operations(self) -> bool:
        """Проверить возможность выполнения CRUD операций."""
        self.print_header("6. Проверка CRUD операций")
        
        try:
            # CREATE
            test_id = uuid4()
            subscription = Subscription(
                id=test_id,
                email="test@example.com",
                city="Moscow"
            )
            self.session.add(subscription)
            self.session.commit()
            self.print_check("CREATE операция", True)
            
            # READ
            retrieved = self.session.query(Subscription).filter_by(id=test_id).first()
            read_ok = retrieved is not None and retrieved.email == "test@example.com"
            self.print_check("READ операция", read_ok)
            
            # UPDATE
            retrieved.city = "Saint Petersburg"
            self.session.commit()
            updated = self.session.query(Subscription).filter_by(id=test_id).first()
            update_ok = updated.city == "Saint Petersburg"
            self.print_check("UPDATE операция", update_ok)
            
            # DELETE
            self.session.delete(updated)
            self.session.commit()
            deleted = self.session.query(Subscription).filter_by(id=test_id).first()
            delete_ok = deleted is None
            self.print_check("DELETE операция", delete_ok)
            
            return read_ok and update_ok and delete_ok
        except SQLAlchemyError as e:
            self.print_check("CRUD операции", False, str(e))
            return False

    def check_unique_constraint(self) -> bool:
        """Проверить работу unique constraint."""
        self.print_header("7. Проверка unique constraint")
        
        try:
            # Добавить первую подписку
            sub1 = Subscription(
                id=uuid4(),
                email="duplicate@example.com",
                city="Moscow"
            )
            self.session.add(sub1)
            self.session.commit()
            
            # Попытаться добавить дублирующуюся подписку
            sub2 = Subscription(
                id=uuid4(),
                email="duplicate@example.com",
                city="Moscow"
            )
            self.session.add(sub2)
            
            try:
                self.session.commit()
                # Если коммит прошел, constraint не работает
                self.print_check("Unique constraint работает", False, "Дублирующаяся подписка была добавлена")
                # Очистить данные
                self.session.query(Subscription).filter_by(email="duplicate@example.com").delete()
                self.session.commit()
                return False
            except SQLAlchemyError:
                # Constraint сработал, как и ожидалось
                self.session.rollback()
                self.print_check("Unique constraint работает", True)
                # Очистить данные
                self.session.query(Subscription).filter_by(email="duplicate@example.com").delete()
                self.session.commit()
                return True
        except SQLAlchemyError as e:
            self.print_check("Unique constraint работает", False, str(e))
            return False

    def run_all_checks(self) -> bool:
        """Запустить все проверки."""
        print("\n" + "="*60)
        print("  SMOKE-CHECK: Проверка миграций Alembic")
        print("="*60)
        
        try:
            # Запустить все проверки
            self.check_database_connection()
            self.check_table_exists()
            self.check_table_structure()
            self.check_indexes()
            self.check_constraints()
            self.check_crud_operations()
            self.check_unique_constraint()
            
            # Вывести итоги
            self.print_header("ИТОГИ")
            total = self.checks_passed + self.checks_failed
            print(f"✅ Пройдено: {self.checks_passed}/{total}")
            print(f"❌ Ошибок: {self.checks_failed}/{total}")
            
            if self.checks_failed == 0:
                print("\n🎉 Все проверки пройдены успешно!")
                return True
            else:
                print(f"\n⚠️  Обнаружено {self.checks_failed} ошибок")
                return False
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            return False
        finally:
            self.session.close()


def main():
    """Главная функция."""
    checker = MigrationChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
