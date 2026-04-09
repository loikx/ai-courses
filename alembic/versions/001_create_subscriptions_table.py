"""create_subscriptions_table

Revision ID: 001
Revises: 
Create Date: 2026-03-19 18:42:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')

    # Создание таблицы subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', 'city', name='uq_subscription_email_city')
    )
    
    # Создание индексов
    op.create_index('idx_subscriptions_email', 'subscriptions', ['email'], unique=False)
    op.create_index('idx_subscriptions_city', 'subscriptions', ['city'], unique=False)


def downgrade() -> None:
    # Удаление индексов
    op.drop_index('idx_subscriptions_city', table_name='subscriptions')
    op.drop_index('idx_subscriptions_email', table_name='subscriptions')
    
    # Удаление таблицы
    op.drop_table('subscriptions')
