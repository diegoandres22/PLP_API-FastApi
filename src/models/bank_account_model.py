import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID

from src.db.base import Base


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pay_method = Column(String, nullable=False)
    holder_name_cta = Column(String, nullable=True)
    # Cédula/RIF y número de cuenta son IDENTIFICADORES, no cantidades: como
    # Float perdían precisión (un número de cuenta de 20 dígitos no cabe en un
    # double sin redondear) y se comían los ceros a la izquierda.
    document_name = Column(String, nullable=True)
    number_cta_1 = Column(String, nullable=True)
    number_cta_2 = Column(String, nullable=True)
    email_cta = Column(String, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
