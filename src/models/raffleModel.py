from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from src.db.db import engine
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class Raffle(Base):
    __tablename__ = 'raffles'

    # Información base
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String, nullable=False)  # Título de la rifa
    description = Column(String, nullable=False)  # Descripción general de la rifa
    image = Column(String, nullable=False)  # URL de la imagen de la rifa
    ticket_price = Column(Float, nullable=False)  # Precio de cada boleto
    min_purchase = Column(Float, nullable=False)  # Mínimo de boletos que se deben comprar
    raffle_status = Column(Integer, nullable=False)  # Estado numérico de la rifa
    state = Column(Boolean, default=True)  # Estado activo o inactivo

    # Premios
    trophy = Column(String, nullable=False)  # Premio principal
    secondPrize = Column(String, nullable=False)  # Segundo premio
    additionalPrize = Column(String, nullable=False)  # Premios adicionales
    premium_ticket1 = Column(Integer, nullable=True)  # Boleto premiado 1
    premium_ticket2 = Column(Integer, nullable=True)  # Boleto premiado 2
    premium_ticket3 = Column(Integer, nullable=True)  # Boleto premiado 3
    premium_ticket4 = Column(Integer, nullable=True)  # Boleto premiado 4
    premium_ticket5 = Column(Integer, nullable=True)  # Boleto premiado 5
    premium_ticket6 = Column(Integer, nullable=True)  # Boleto premiado 6

    # Boletos
    total_tickets = Column(Integer, nullable=True)  # Total de boletos disponibles
    tickets_sold = Column(Integer, default=0)  # Boletos vendidos

    # Fechas
    lottery_date = Column(DateTime, nullable=True)  # Fecha del sorteo

    # Metadatos
    created_by = Column(String, nullable=True)  # Usuario que creó la rifa
    updated_by = Column(String, nullable=True)  # Último usuario que modificó

    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Fecha de creación
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # Fecha de última actualización


Base.metadata.create_all(bind=engine)