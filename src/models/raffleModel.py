from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base

from src.db.db import engine

Base = declarative_base()

class Raffle(Base):
    __tablename__ = "raffles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(Boolean, default=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String, nullable=True)
    ticket_price = Column(Float, nullable=False)
    min_purchase = Column(Float, nullable=False)
    raffle_status = Column(Integer, nullable=False)
    countdown_time = Column(String, nullable=False)
    progress_percentage = Column(Float, nullable=False)
    tickets_account_premium = Column(Integer, nullable=False)

Base.metadata.create_all(bind=engine)
