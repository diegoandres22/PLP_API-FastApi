from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import List, Optional
from datetime import datetime

class PurchaseCreate(BaseModel):
    buyer_email: EmailStr 
    raffle_id: UUID
    ticket_count: int
    payment_method: str 
    payment_reference: str 
    full_name: str
    phone_number: str
    holder_cta_bank: str
    image_url: Optional[str] = None
    

class TicketsByRaffleResponse(BaseModel):
    raffle_id: UUID
    ticket_numbers: List[int]


class PublicPurchaseResponse(BaseModel):
    """Respuesta para endpoints públicos (sin login): nunca incluir PII del
    comprador (nombre, teléfono, email, referencia de pago, comprobante)."""
    id: UUID
    raffle_id: UUID
    raffle_title: Optional[str] = None
    ticket_numbers: List[int]
    purchase_date: datetime
    is_confirmed: Optional[bool] = None

    model_config = {
        "from_attributes": True
    }


class PurchaseResponse(BaseModel):
    id: UUID
    raffle_id: UUID
    raffle_title: Optional[str] = None
    buyer_email: EmailStr 
    ticket_numbers: List[int]
    total_paid: float
    payment_method: str
    payment_reference: str
    purchase_date: datetime
    full_name: str
    phone_number: str
    holder_cta_bank: str
    is_confirmed: Optional[bool] = None
    image_url: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    confirmed_by: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
    


class PurchaseConfirmResponse(BaseModel):
    id: UUID
    raffle_id: UUID
    raffle_title: str
    buyer_email: EmailStr 
    ticket_numbers: List[int]
    total_paid: float
    payment_method: str
    payment_reference: str
    purchase_date: datetime
    full_name: str
    phone_number: str
    holder_cta_bank: str
    is_confirmed: bool
    image_url: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    confirmed_by: Optional[str] = None

    model_config = {
        "from_attributes": True
    }