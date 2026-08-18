from datetime import datetime
from typing import List, Optional
from uuid import UUID as UUIDType

from pydantic import BaseModel


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
    # En Pydantic v2, `Optional[int]` SIN `= None` es requerido-y-nullable: el
    # cliente estaba obligado a enviar el campo aunque fuera null. Con default
    # sí son opcionales de verdad.
    premium_ticket1: Optional[int] = None
    premium_ticket2: Optional[int] = None
    premium_ticket3: Optional[int] = None
    premium_ticket4: Optional[int] = None
    premium_ticket5: Optional[int] = None
    premium_ticket6: Optional[int] = None
    total_tickets: int
    lottery_date: datetime
    created_by: str


class RaffleUpdate(BaseModel):
    # Actualización parcial: todo opcional, se aplica con exclude_unset.
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    ticket_price: Optional[float] = None
    min_purchase: Optional[float] = None
    raffle_status: Optional[int] = None
    state: Optional[bool] = None

    trophy: Optional[str] = None
    secondPrize: Optional[str] = None
    additionalPrize: Optional[str] = None
    premium_ticket1: Optional[int] = None
    premium_ticket2: Optional[int] = None
    premium_ticket3: Optional[int] = None
    premium_ticket4: Optional[int] = None
    premium_ticket5: Optional[int] = None
    premium_ticket6: Optional[int] = None

    total_tickets: Optional[int] = None

    # tickets_sold_list ya NO se acepta por API: era editable vía PUT y
    # sobrescribirla desde fuera rompe la invariante de la reserva atómica
    # (podía "liberar" boletos ya vendidos y revenderlos). Solo la modifica
    # create_purchase dentro de su transacción con lock.

    lottery_date: Optional[datetime] = None

    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class RaffleOut(BaseModel):
    id: UUIDType
    title: str
    description: str
    image: Optional[str] = None
    ticket_price: float
    min_purchase: float
    raffle_status: int
    state: Optional[bool] = None
    trophy: str
    secondPrize: str
    additionalPrize: str
    premium_ticket1: Optional[int] = None
    premium_ticket2: Optional[int] = None
    premium_ticket3: Optional[int] = None
    premium_ticket4: Optional[int] = None
    premium_ticket5: Optional[int] = None
    premium_ticket6: Optional[int] = None
    total_tickets: Optional[int] = None
    tickets_sold_list: List[int] = []
    lottery_date: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
