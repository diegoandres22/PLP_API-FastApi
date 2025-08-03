from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import List
from datetime import datetime

class PurchaseCreate(BaseModel):
    email: EmailStr
    raffle_id: UUID
    ticket_count: int
    payment_method: str 
    payment_reference: str 

class PurchaseResponse(BaseModel):
    id: UUID
    raffle_id: UUID
    raffle_title: str
    email: EmailStr
    ticket_numbers: List[int]
    total_paid: float
    payment_method: str
    payment_ref: str
    purchase_date: datetime

class Config:
        orm_mode = True
