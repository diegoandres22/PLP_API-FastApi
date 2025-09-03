import uuid
from sqlalchemy import Column, String, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from src.db.db import engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pay_method = Column(String, nullable=False)  
    holder_name_cta = Column(String, nullable=True)
    document_name = Column(Float, nullable=True)
    number_cta_1 = Column(Float, nullable=True)
    number_cta_2 = Column(String, nullable=True)
    email_cta = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)