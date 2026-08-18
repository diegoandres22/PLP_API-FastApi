import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from src.db.base import Base


class Purchase(Base):
    __tablename__ = 'purchases'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    ticket_numbers = Column(ARRAY(Integer), nullable=False)               # Números comprados
    total_paid = Column(Float, nullable=False)                            # Monto pagado
    payment_method = Column(String, nullable=False)                       # Tipo: Transferencia, Zelle...
    payment_reference = Column(String, nullable=False)                    # Referencia de pago
    purchase_date = Column(DateTime, default=func.now())                  # Fecha de compra
    raffle_id = Column(UUID(as_uuid=True), nullable=False, index=True)    # Relación con la rifa
    buyer_email = Column(String, nullable=False, index=True)              # Correo del comprador
    full_name = Column(String, nullable=False)                            # Nombre completo del comprador
    phone_number = Column(String, nullable=False)                         # Teléfono del comprador
    holder_cta_bank = Column(String, nullable=False)                      # Titular de la cuenta bancaria
    is_confirmed = Column(Boolean, nullable=True, default=None)
    image_url = Column(String, nullable=True)                             # URL del comprobante
    confirmed_at = Column(DateTime, nullable=True)                        # Fecha de confirmación
    confirmed_by = Column(String, nullable=True)                          # Admin que confirmó/rechazó
