"""Corrige tipos de columnas e índices de integridad

1. raffles.tickets_sold_list: text[] -> integer[]
   Es la causa raíz del bug de boletos revendidos: al volver de la BD como
   texto, restar el conjunto de vendidos al de disponibles no eliminaba nada
   ({0,1,2,...} - {"1","2"} = {0,1,2,...}) y los mismos números se volvían a
   sortear. Los datos existentes se convierten con USING, sin pérdida.

2. bank_accounts.document_name / number_cta_1: double precision -> varchar
   Cédula/RIF y número de cuenta son identificadores, no cantidades: como
   float perdían precisión y ceros a la izquierda.

3. Índices en purchases(raffle_id) y purchases(buyer_email), que se recorren
   en cada listado y en la validación de boletos por correo.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- 1. tickets_sold_list: text[] -> integer[] ---------------------
    # Primero se normalizan los NULL para poder dejar la columna NOT NULL.
    op.execute("UPDATE raffles SET tickets_sold_list = '{}' WHERE tickets_sold_list IS NULL")
    op.alter_column(
        "raffles",
        "tickets_sold_list",
        existing_type=postgresql.ARRAY(sa.String()),
        type_=postgresql.ARRAY(sa.Integer()),
        postgresql_using="tickets_sold_list::integer[]",
        existing_nullable=True,
        nullable=False,
        server_default=sa.text("'{}'::integer[]"),
    )

    # --- 2. Identificadores bancarios a texto --------------------------
    # ::bigint::text evita que un 12345678 termine como "12345678.0".
    op.alter_column(
        "bank_accounts",
        "document_name",
        existing_type=sa.Float(),
        type_=sa.String(),
        postgresql_using="document_name::bigint::text",
        existing_nullable=True,
    )
    op.alter_column(
        "bank_accounts",
        "number_cta_1",
        existing_type=sa.Float(),
        type_=sa.String(),
        postgresql_using="number_cta_1::bigint::text",
        existing_nullable=True,
    )

    op.execute("UPDATE bank_accounts SET is_active = false WHERE is_active IS NULL")
    op.alter_column(
        "bank_accounts",
        "is_active",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("false"),
    )

    # --- 3. Índices ----------------------------------------------------
    op.create_index("ix_purchases_raffle_id", "purchases", ["raffle_id"])
    op.create_index("ix_purchases_buyer_email", "purchases", ["buyer_email"])


def downgrade() -> None:
    op.drop_index("ix_purchases_buyer_email", table_name="purchases")
    op.drop_index("ix_purchases_raffle_id", table_name="purchases")

    op.alter_column(
        "bank_accounts",
        "is_active",
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None,
    )
    op.alter_column(
        "bank_accounts",
        "number_cta_1",
        existing_type=sa.String(),
        type_=sa.Float(),
        postgresql_using="number_cta_1::double precision",
        existing_nullable=True,
    )
    op.alter_column(
        "bank_accounts",
        "document_name",
        existing_type=sa.String(),
        type_=sa.Float(),
        postgresql_using="document_name::double precision",
        existing_nullable=True,
    )

    op.alter_column(
        "raffles",
        "tickets_sold_list",
        existing_type=postgresql.ARRAY(sa.Integer()),
        type_=postgresql.ARRAY(sa.String()),
        postgresql_using="tickets_sold_list::text[]",
        existing_nullable=False,
        nullable=True,
        server_default=None,
    )
