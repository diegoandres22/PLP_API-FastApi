from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from src.db.db import engine
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

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

    tickets_sold_list = Column(ARRAY(String), default=[])

    lottery_date = Column(DateTime, nullable=True)

    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

Base.metadata.create_all(bind=engine)
