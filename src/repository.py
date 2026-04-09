"""
Repository pattern для работы с подписками.

Этот модуль содержит:
- SubscriptionRepository класс для CRUD операций
- Методы для работы с подписками в БД
"""

from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .db_models import Subscription
from .models import SubscriptionData


class SubscriptionRepository:
    """
    Repository для работы с подписками в БД.
    
    Методы:
        create: Создать новую подписку
        get_by_id: Получить подписку по ID
        get_all: Получить все подписки
        delete: Удалить подписку по ID
        get_by_email_and_city: Получить подписку по email и городу
    """

    def __init__(self, db: Session):
        """
        Инициализация repository.
        
        Args:
            db: SQLAlchemy сессия
        """
        self.db = db

    def create(self, email: str, city: str) -> SubscriptionData:
        """
        Создать новую подписку.
        
        Args:
            email: Email подписчика
            city: Город для подписки
            
        Returns:
            SubscriptionData: Созданная подписка
            
        Raises:
            IntegrityError: Если подписка уже существует (нарушение UNIQUE constraint)
        """
        subscription = Subscription(email=email, city=city)
        self.db.add(subscription)
        try:
            self.db.commit()
            self.db.refresh(subscription)
        except IntegrityError:
            self.db.rollback()
            raise
        
        return self._to_pydantic(subscription)

    def get_by_id(self, subscription_id: UUID) -> SubscriptionData | None:
        """
        Получить подписку по ID.
        
        Args:
            subscription_id: UUID подписки
            
        Returns:
            SubscriptionData или None если не найдена
        """
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        return self._to_pydantic(subscription) if subscription else None

    def get_all(self) -> list[SubscriptionData]:
        """
        Получить все подписки.
        
        Returns:
            Список всех подписок
        """
        subscriptions = self.db.query(Subscription).all()
        return [self._to_pydantic(sub) for sub in subscriptions]

    def delete(self, subscription_id: UUID) -> SubscriptionData | None:
        """
        Удалить подписку по ID.
        
        Args:
            subscription_id: UUID подписки
            
        Returns:
            Удалённая подписка или None если не найдена
        """
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            return None
        
        self.db.delete(subscription)
        deleted_subscription = self._to_pydantic(subscription)
        self.db.commit()
        
        return deleted_subscription

    def get_by_email_and_city(self, email: str, city: str) -> SubscriptionData | None:
        """
        Получить подписку по email и городу.
        
        Args:
            email: Email подписчика
            city: Город
            
        Returns:
            SubscriptionData или None если не найдена
        """
        subscription = self.db.query(Subscription).filter(
            Subscription.email == email,
            Subscription.city == city
        ).first()
        
        return self._to_pydantic(subscription) if subscription else None

    @staticmethod
    def _to_pydantic(subscription: Subscription) -> SubscriptionData:
        """
        Преобразовать SQLAlchemy модель в Pydantic модель.
        
        Args:
            subscription: SQLAlchemy Subscription модель
            
        Returns:
            SubscriptionData: Pydantic модель
        """
        return SubscriptionData(
            id=str(subscription.id),
            email=subscription.email,
            city=subscription.city,
            created_at=subscription.created_at
        )
