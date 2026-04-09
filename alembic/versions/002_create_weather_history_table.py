"""create_weather_history_table

Revision ID: 002
Revises: 001
Create Date: 2026-04-09 18:10:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание таблицы для сохранённой истории погоды по дням.
    op.create_table(
        "weather_history",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("temp", sa.Float(), nullable=False),
        sa.Column("condition", sa.String(length=100), nullable=False),
        sa.Column("humidity", sa.Integer(), nullable=False),
        sa.Column("wind_speed", sa.Float(), nullable=False),
        sa.Column("pressure", sa.Integer(), nullable=False),
        sa.Column(
            "fetched_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("city", "date", name="uq_weather_history_city_date"),
    )

    op.create_index("idx_weather_history_city", "weather_history", ["city"], unique=False)
    op.create_index(
        "idx_weather_history_city_date",
        "weather_history",
        ["city", "date"],
        unique=False,
    )


def downgrade() -> None:
    # Откат таблицы истории погоды и сопутствующих индексов.
    op.drop_index("idx_weather_history_city_date", table_name="weather_history")
    op.drop_index("idx_weather_history_city", table_name="weather_history")
    op.drop_table("weather_history")
