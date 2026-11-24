"""Add persisted recommendation filters.

Revision ID: 20261116_0002
Revises: 20261112_0001
Create Date: 2026-11-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261116_0002"
down_revision: str | None = "20261112_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_catalog_items_price_unit", "catalog_items", type_="check")
    op.create_check_constraint(
        "ck_catalog_items_price_unit",
        "catalog_items",
        "price_unit IN ('item', 'person', 'ticket', 'hour', 'service')",
    )
    op.create_table(
        "recommendation_filters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("organization_type_id", sa.Uuid(), nullable=True),
        sa.Column("budget", sa.Numeric(12, 2), nullable=True),
        sa.Column("party_size", sa.Integer(), nullable=True),
        sa.Column("city", sa.String(120), nullable=True),
        sa.Column("wishes", sa.String(500), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "budget IS NULL OR budget >= 0",
            name="ck_filters_budget_nonnegative",
        ),
        sa.CheckConstraint(
            "party_size IS NULL OR party_size BETWEEN 1 AND 20",
            name="ck_filters_party_size",
        ),
        sa.CheckConstraint("currency = upper(currency)", name="ck_filters_currency_upper"),
        sa.ForeignKeyConstraint(
            ["organization_type_id"],
            ["organization_types.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_recommendation_filters_client_id",
        "recommendation_filters",
        ["client_id"],
    )
    op.create_index(
        "ix_recommendation_filters_created_at",
        "recommendation_filters",
        ["created_at"],
    )
    op.create_index(
        "ix_recommendation_filters_user_id",
        "recommendation_filters",
        ["user_id"],
    )
    op.create_index(
        "ix_recommendation_filters_organization_type_id",
        "recommendation_filters",
        ["organization_type_id"],
    )
    op.create_index(
        "ix_recommendation_filters_city",
        "recommendation_filters",
        ["city"],
    )


def downgrade() -> None:
    op.drop_table("recommendation_filters")
    op.drop_constraint("ck_catalog_items_price_unit", "catalog_items", type_="check")
    op.create_check_constraint(
        "ck_catalog_items_price_unit",
        "catalog_items",
        "price_unit IN ('item', 'person', 'hour', 'service')",
    )
