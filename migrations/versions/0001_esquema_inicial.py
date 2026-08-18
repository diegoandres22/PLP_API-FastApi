"""Esquema inicial (baseline)

Refleja el esquema tal como lo creaba Base.metadata.create_all() antes de
introducir Alembic.

  - BD NUEVA (vacía):      alembic upgrade head        -> crea todo
  - BD YA EXISTENTE:       alembic stamp 0001          -> marca como aplicada
                           alembic upgrade head        -> aplica solo 0002

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "raffles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("image", sa.String(), nullable=False),
        sa.Column("ticket_price", sa.Float(), nullable=False),
        sa.Column("min_purchase", sa.Float(), nullable=False),
        sa.Column("raffle_status", sa.Integer(), nullable=False),
        sa.Column("state", sa.Boolean(), nullable=True),
        sa.Column("trophy", sa.String(), nullable=False),
        sa.Column("secondPrize", sa.String(), nullable=False),
        sa.Column("additionalPrize", sa.String(), nullable=False),
        sa.Column("premium_ticket1", sa.Integer(), nullable=True),
        sa.Column("premium_ticket2", sa.Integer(), nullable=True),
        sa.Column("premium_ticket3", sa.Integer(), nullable=True),
        sa.Column("premium_ticket4", sa.Integer(), nullable=True),
        sa.Column("premium_ticket5", sa.Integer(), nullable=True),
        sa.Column("premium_ticket6", sa.Integer(), nullable=True),
        sa.Column("total_tickets", sa.Integer(), nullable=True),
        sa.Column("tickets_sold_list", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("lottery_date", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("updated_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )

    op.create_table(
        "purchases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ticket_numbers", postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.Column("total_paid", sa.Float(), nullable=False),
        sa.Column("payment_method", sa.String(), nullable=False),
        sa.Column("payment_reference", sa.String(), nullable=False),
        sa.Column("purchase_date", sa.DateTime(), nullable=True),
        sa.Column("raffle_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("buyer_email", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("phone_number", sa.String(), nullable=False),
        sa.Column("holder_cta_bank", sa.String(), nullable=False),
        sa.Column("is_confirmed", sa.Boolean(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("confirmed_by", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )

    op.create_table(
        "bank_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pay_method", sa.String(), nullable=False),
        sa.Column("holder_name_cta", sa.String(), nullable=True),
        sa.Column("document_name", sa.Float(), nullable=True),
        sa.Column("number_cta_1", sa.Float(), nullable=True),
        sa.Column("number_cta_2", sa.String(), nullable=True),
        sa.Column("email_cta", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("bank_accounts")
    op.drop_table("purchases")
    op.drop_table("raffles")
