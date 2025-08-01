# src/services/raffle_service.py

from sqlalchemy.orm import Session
from src.models.raffleModel import Raffle

def get_raffles_endpoint(db: Session):
    raffles = db.query(Raffle).all()
    return {"Rifas": [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "image": r.image,
            "ticket_price": r.ticket_price,
            "min_purchase": r.min_purchase,
            "raffle_status": r.raffle_status,
            "countdown_time": r.countdown_time,
            "progress_percentage": r.progress_percentage,
            "tickets_account_premium": r.tickets_account_premium,
            "state": r.state
        } for r in raffles]
    }

def create_raffle_endpoint(db: Session, **data):
    raffle = Raffle(**data)
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

def update_raffle_endpoint(db: Session, raffle_id: int, **data):
    raffle = db.query(Raffle).filter(Raffle.id == raffle_id).first()
    if not raffle:
        return {"error": "Rifa no encontrada"}
    
    for field, value in data.items():
        if value is not None:
            setattr(raffle, field, value)

    db.commit()
    db.refresh(raffle)
    return {"message": "Rifa actualizada con éxito", "raffle": {"id": raffle.id, "title": raffle.title}}
