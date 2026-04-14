"""Add payment_provider and external_payment_id to orders

Revision ID: f4e3d2c1b0a9
Revises: b3f9a2c11d8e
Create Date: 2026-04-14
"""
from alembic import op
import sqlalchemy as sa

revision = "f4e3d2c1b0a9"
down_revision = "b3f9a2c11d8e"
branch_labels = None
depends_on = None

provider_enum = sa.Enum(
    "STRIPE", "YOCO", "PAYJUSTNOW", "PAYFLEX", "HAPPYPAY",
    name="paymentprovider",
)


def upgrade() -> None:
    provider_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "orders",
        sa.Column(
            "payment_provider",
            provider_enum,
            nullable=False,
            server_default="STRIPE",
        ),
    )
    op.add_column(
        "orders",
        sa.Column("external_payment_id", sa.String(length=200), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("orders", "external_payment_id")
    op.drop_column("orders", "payment_provider")
    provider_enum.drop(op.get_bind(), checkfirst=True)
