import uuid
from sqlalchemy import Column, Float, DateTime, ForeignKey, Integer, String, func, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base
from src.db.db import engine
from sqlalchemy.dialects.postgresql import UUID



Base = declarative_base()

class Purchase(Base):
    __tablename__ = 'purchases'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,  unique=True, nullable=False)  # ID único
    ticket_numbers = Column(ARRAY(Integer), nullable=False)               # Números comprados
    total_paid = Column(Float, nullable=False)                            # Monto pagado
    payment_method = Column(String, nullable=False)                       # Tipo: Transferencia, Zelle...
    payment_ref = Column(String, nullable=False)                           # Referencia de pago
    purchase_date = Column(DateTime, default=func.now())                  # Fecha de compra
    raffle_id = Column(String, nullable=False)                          # ID DE Relación con la rifa
    buyer_email = Column(String, nullable=False)                          # Correo del comprador
    full_name = Column(String, nullable=False)                              # Nombre completo del comprador
    phone_number = Column(String, nullable=False)                           # Teléfono del comprador
    holder_cta_bank = Column(String, nullable=False)                         # Titular de la cuenta bancaria
    is_confirmed = Column(Boolean, default=False)                            # Estado de confirmación
    image_url = Column(String, nullable=True)                               # URL de la imagen

Base.metadata.create_all(bind=engine)