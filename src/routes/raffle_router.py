from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.deps import get_db
from src.services import raffle_service
from src.schemas.raffle_schema import RaffleCreate
from src.schemas.raffle_schema import RaffleUpdate


router = APIRouter()

@router.get("/all/")
def get_all_raffles(db: Session = Depends(get_db)):
    return raffle_service.get_raffles_endpoint(db)

@router.post("/new/")
async def create_raffle_endpoint(
    data: RaffleCreate,
    db: Session = Depends(get_db)
):
    return raffle_service.create_raffle(data, db)

@router.get("/{raffle_id}")
def get_raffle_by_id(raffle_id: int, db: Session = Depends(get_db)):
    return raffle_service.get_raffle_by_id_endpoint(db, raffle_id)

@router.delete("/{raffle_id}")
def delete_raffle(raffle_id: int, db: Session = Depends(get_db)):
    return raffle_service.delete_raffle_endpoint(db, raffle_id)

@router.put("/{raffle_id}")
def update_raffle(
    raffle_id: int,
    data: RaffleUpdate,
    db: Session = Depends(get_db)
):
    return raffle_service.update_raffle_endpoint(db, raffle_id, data)