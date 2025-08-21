
from sqlalchemy.orm import Session
from src.schemas.raffle_schema import RaffleCreate, RaffleUpdate
from src.crud.raffle_crud import (
    get_all_raffles,
    get_raffle_by_id,
    crud_create_raffle as crud_create_raffle,
    update_raffle as crud_update_raffle,
    delete_raffle as crud_delete_raffle,
)
from uuid import UUID as UUIDType


def get_raffles_endpoint(db: Session):
    raffles = get_all_raffles(db)
    return {"Rifas": [r.__dict__ for r in raffles]}
    
def create_raffle(data: RaffleCreate, db: Session, image_url: str):
    data_dict = data.dict()
    data_dict["image"] = image_url
    raffle = crud_create_raffle(db, data_dict)
    return {"Rifa creada": {"id": raffle.id, "title": raffle.title}}


def get_raffle_by_id_endpoint(db: Session, raffle_id: UUIDType):
    raffle = get_raffle_by_id(db, raffle_id)
    if raffle:
        return raffle
    return {"error": "Rifa no encontrada"}

def delete_raffle_endpoint(db: Session, raffle_id: UUIDType):
    result = crud_delete_raffle(db, raffle_id)
    if not result:
        return {"error": "Rifa no encontrada"}
    return {"message": "Rifa eliminada con éxito"}

def update_raffle_endpoint(db: Session, raffle_id: UUIDType, data: RaffleUpdate):
    raffle = crud_update_raffle(db, raffle_id, data)
    if not raffle:
        return {"error": "Rifa no encontrada"}
    return {"message": "Rifa actualizada con éxito", "raffle": {"id": raffle.id, "title": raffle.title}}

