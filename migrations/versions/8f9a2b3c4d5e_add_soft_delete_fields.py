"""Add soft delete fields to products and categories

Revision ID: 8f9a2b3c4d5e
Revises: 7446947a531a
Create Date: 2026-01-04 22:00:00.000000

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "8f9a2b3c4d5e"
down_revision = "0ada6921b672"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add deleted_at column to categories table
    op.add_column(
        "categories",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Add deleted_at column to products table
    op.add_column(
        "products",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    # Remove deleted_at column from products table
    op.drop_column("products", "deleted_at")

    # Remove deleted_at column from categories table
    op.drop_column("categories", "deleted_at")
