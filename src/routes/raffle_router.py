# src/routes/raffle.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.deps import get_db
from src.services import raffle_service

router = APIRouter()

@router.get("/all/")
def get_all_raffles(db: Session = Depends(get_db)):
    return raffle_service.get_raffles_endpoint(db)

@router.post("/new/")
def create_raffle(
    title: str,
    description: str,
    image: str,
    ticket_price: float,
    min_purchase: float,
    raffle_status: int,
    countdown_time: str,
    progress_percentage: float,
    tickets_account_premium: int,
    state: bool,
    db: Session = Depends(get_db)
):
    return raffle_service.create_raffle_endpoint(db,
        title=title,
        description=description,
        image=image,
        ticket_price=ticket_price,
        min_purchase=min_purchase,
        raffle_status=raffle_status,
        countdown_time=countdown_time,
        progress_percentage=progress_percentage,
        tickets_account_premium=tickets_account_premium,
        state=state
    )

@router.get("/{raffle_id}")
def get_raffle_by_id(raffle_id: int, db: Session = Depends(get_db)):
    return raffle_service.get_raffle_by_id_endpoint(db, raffle_id)

@router.delete("/{raffle_id}")
def delete_raffle(raffle_id: int, db: Session = Depends(get_db)):
    return raffle_service.delete_raffle_endpoint(db, raffle_id)

@router.put("/{raffle_id}")
def update_raffle(
    raffle_id: int,
    title: str = None,
    description: str = None,
    image: str = None,
    ticket_price: float = None,
    min_purchase: float = None,
    raffle_status: int = None,
    countdown_time: str = None,
    progress_percentage: float = None,
    tickets_account_premium: int = None,
    state: bool = None,
    db: Session = Depends(get_db)
):
    return raffle_service.update_raffle_endpoint(db, raffle_id,
        title=title,
        description=description,
        image=image,
        ticket_price=ticket_price,
        min_purchase=min_purchase,
        raffle_status=raffle_status,
        countdown_time=countdown_time,
        progress_percentage=progress_percentage,
        tickets_account_premium=tickets_account_premium,
        state=state
    )
