
from sqlalchemy.orm import Session
from src.models.raffleModel import Raffle
from src.schemas.raffle_schema import RaffleCreate
from src.schemas.raffle_schema import RaffleUpdate


def get_raffles_endpoint(db: Session):
    raffles = db.query(Raffle).all()
    return {"Rifas": [r.__dict__ for r in raffles]}  


def create_raffle(data: RaffleCreate, db: Session):
    raffle = Raffle(**data.dict())
    db.add(raffle)
    db.commit()
    db.refresh(raffle)
    return {"Rifa creada": {"id": raffle.id, "title": raffle.title}}



def get_raffle_by_id_endpoint(db: Session, raffle_id: int):
    raffle = db.query(Raffle).filter(Raffle.id == raffle_id).first()
    if raffle:
        return raffle
    return {"error": "Rifa no encontrada"}

def delete_raffle_endpoint(db: Session, raffle_id: int):
    raffle = db.query(Raffle).filter(Raffle.id == raffle_id).first()
    if not raffle:
        return {"error": "Rifa no encontrada"}
    db.delete(raffle)
    db.commit()
    return {"message": "Rifa eliminada con éxito"}

def update_raffle_endpoint(db: Session, raffle_id: int, data: RaffleUpdate):
    raffle = db.query(Raffle).filter(Raffle.id == raffle_id).first()
    if not raffle:
        return {"error": "Rifa no encontrada"}

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(raffle, field, value)

    db.commit()
    db.refresh(raffle)
    return {"message": "Rifa actualizada con éxito", "raffle": {"id": raffle.id, "title": raffle.title}}