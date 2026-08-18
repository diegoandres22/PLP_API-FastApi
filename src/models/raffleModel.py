import uuid

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.db.base import Base


class Raffle(Base):
    __tablename__ = 'raffles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String, nullable=False)
    ticket_price = Column(Float, nullable=False)
    min_purchase = Column(Float, nullable=False)
    raffle_status = Column(Integer, nullable=False)
    state = Column(Boolean, default=True)

    trophy = Column(String, nullable=False)
    secondPrize = Column(String, nullable=False)
    additionalPrize = Column(String, nullable=False)
    premium_ticket1 = Column(Integer, nullable=True)
    premium_ticket2 = Column(Integer, nullable=True)
    premium_ticket3 = Column(Integer, nullable=True)
    premium_ticket4 = Column(Integer, nullable=True)
    premium_ticket5 = Column(Integer, nullable=True)
    premium_ticket6 = Column(Integer, nullable=True)

    total_tickets = Column(Integer, nullable=True)

    # ARRAY(Integer), no ARRAY(String): los boletos son números y se comparan
    # contra purchases.ticket_numbers (ARRAY(Integer)). Cuando esto era texto,
    # restar el conjunto de vendidos al de disponibles no eliminaba nada
    # ({0,1,2...} - {"1","2"} = {0,1,2...}) y se revendían boletos.
    tickets_sold_list = Column(ARRAY(Integer), nullable=False, server_default="{}", default=list)

    lottery_date = Column(DateTime, nullable=True)

    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
