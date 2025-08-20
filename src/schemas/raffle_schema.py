from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID as UUIDType


class RaffleCreate(BaseModel):
    title: str
    description: str
    ticket_price: float
    min_purchase: float
    raffle_status: int
    state: bool
    trophy: str
    secondPrize: str
    additionalPrize: str
    premium_ticket1: Optional[int]
    premium_ticket2: Optional[int]
    premium_ticket3: Optional[int]
    premium_ticket4: Optional[int]
    premium_ticket5: Optional[int]
    premium_ticket6: Optional[int]
    total_tickets: int
    lottery_date: datetime
    created_by: str

class RaffleUpdate(BaseModel):
    # Información base
    title: Optional[str]
    description: Optional[str]
    image: Optional[str]
    ticket_price: Optional[float]
    min_purchase: Optional[float]
    raffle_status: Optional[int]
    state: Optional[bool]

    # Premios
    trophy: Optional[str]
    secondPrize: Optional[str]
    additionalPrize: Optional[str]
    premium_ticket1: Optional[int]
    premium_ticket2: Optional[int]
    premium_ticket3: Optional[int]
    premium_ticket4: Optional[int]
    premium_ticket5: Optional[int]
    premium_ticket6: Optional[int]

    # Boletos
    total_tickets: Optional[int]
    tickets_sold_list: Optional[List[str]]
    
    # Fechas
    lottery_date: Optional[datetime]

    # Metadatos
    created_by: Optional[str]
    updated_by: Optional[str]

class RaffleOut(RaffleCreate):
    id: UUIDType  # ID único
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    tickets_sold_list: List[str] = []

    class Config:
        from_attributes = True
