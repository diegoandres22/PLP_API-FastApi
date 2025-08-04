
from sqlalchemy.orm import Session
from src.models.raffleModel import Raffle
from src.schemas.raffle_schema import RaffleCreate, RaffleUpdate
from uuid import UUID as UUIDType
from typing import List 


def get_all_raffles(db: Session):
    return db.query(Raffle).all()

def get_raffle_by_id(db: Session, raffle_id: UUIDType):
    return db.query(Raffle).filter(Raffle.id == raffle_id).first()

def create_raffle(db: Session, data: RaffleCreate):
    raffle = Raffle(**data.dict())
    db.add(raffle)
    db.commit()
    db.refresh(raffle)
    return raffle

def update_raffle(db: Session, raffle_id: UUIDType, data: RaffleUpdate):
    raffle = get_raffle_by_id(db, raffle_id)
    if not raffle:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(raffle, key, value)
    db.commit()
    db.refresh(raffle)
    return raffle

def delete_raffle(db: Session, raffle_id: UUIDType):
    raffle = get_raffle_by_id(db, raffle_id)
    if not raffle:
        return None
    db.delete(raffle)
    db.commit()
    return True

def update_raffle_tickets_sold(db: Session, raffle, new_tickets: list[int]):
    if raffle.tickets_sold_list is None:
        raffle.tickets_sold_list = []

    # Agrega los nuevos tickets sin repetir (por si acaso)
    existing_tickets = set(raffle.tickets_sold_list)
    updated_tickets = list(existing_tickets.union(new_tickets))

    raffle.tickets_sold_list = updated_tickets

    db.commit()
    db.refresh(raffle)