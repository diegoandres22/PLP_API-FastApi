from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID as UUIDType

class RaffleCreate(BaseModel):
    # Información base
    
    title: str  # Título de la rifa
    description: str  # Descripción general de la rifa
    image: str  # URL de la imagen de la rifa
    ticket_price: float  # Precio de cada boleto
    min_purchase: float  # Mínimo de boletos que se deben comprar
    raffle_status: int  # Estado numérico de la rifa
    state: bool  # Estado activo o inactivo

    
    # Premios
    trophy: str  # Premio principal
    secondPrize: str  # Segundo premio
    additionalPrize: str  # Premios adicionales
    premium_ticket1: Optional[int]  # Boleto premiado 1
    premium_ticket2: Optional[int]  # Boleto premiado 2
    premium_ticket3: Optional[int]  # Boleto premiado 3
    premium_ticket4: Optional[int]  # Boleto premiado 4
    premium_ticket5: Optional[int]  # Boleto premiado 5
    premium_ticket6: Optional[int]  # Boleto premiado 6
    
    # Boletos
    total_tickets: int  # Total de boletos disponibles

    # Fechas
    lottery_date: datetime  # Fecha del sorteo

    # Metadatos
    created_by: str  # Usuario que creó la rifa

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
