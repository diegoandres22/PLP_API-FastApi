from pydantic import BaseModel
from typing import Optional

class RaffleCreate(BaseModel):
    title: str
    description: str
    image: str
    ticket_price: float
    min_purchase: float
    raffle_status: int
    countdown_time: str
    progress_percentage: float
    tickets_account_premium: int
    state: bool

class RaffleUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    image: Optional[str]
    ticket_price: Optional[float]
    min_purchase: Optional[float]
    raffle_status: Optional[int]
    countdown_time: Optional[str]
    progress_percentage: Optional[float]
    tickets_account_premium: Optional[int]
    state: Optional[bool]

class RaffleOut(RaffleCreate):
    id: int

    class Config:
        orm_mode = True
