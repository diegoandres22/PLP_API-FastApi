from uuid import UUID as UUIDType

from sqlalchemy.orm import Session

from src.core.errors import ApiError, ErrorCode
from src.crud.raffle_crud import (
    crud_create_raffle,
    delete_raffle as crud_delete_raffle,
    get_all_raffles,
    get_raffle_by_id,
    update_raffle as crud_update_raffle,
)
from src.schemas.raffle_schema import RaffleCreate, RaffleOut, RaffleUpdate


def _to_out(raffle) -> RaffleOut:
    out = RaffleOut.model_validate(raffle)
    # El ordenamiento es presentación: se hace sobre el DTO, no mutando la
    # entidad del ORM (mutarla la marcaba sucia y el próximo commit reescribía
    # la columna como efecto colateral de una lectura).
    out.tickets_sold_list = sorted(out.tickets_sold_list or [])
    return out


def get_raffles_endpoint(db: Session):
    # RaffleOut en vez de r.__dict__: __dict__ filtra el estado interno de
    # SQLAlchemy (_sa_instance_state) dentro de la respuesta JSON.
    return {"Rifas": [_to_out(r) for r in get_all_raffles(db)]}


def create_raffle(data: RaffleCreate, db: Session, image_url: str):
    data_dict = data.model_dump()
    data_dict["image"] = image_url
    raffle = crud_create_raffle(db, data_dict)
    return {"Rifa creada": {"id": raffle.id, "title": raffle.title}}


def get_raffle_by_id_endpoint(db: Session, raffle_id: UUIDType) -> RaffleOut:
    raffle = get_raffle_by_id(db, raffle_id)
    if not raffle:
        # Antes devolvía {"error": ...} con HTTP 200: el frontend no podía
        # distinguir "no existe" de una rifa válida.
        raise ApiError(404, ErrorCode.RAFFLE_NOT_FOUND, "Rifa no encontrada", context={"raffle_id": str(raffle_id)})
    return _to_out(raffle)


def delete_raffle_endpoint(db: Session, raffle_id: UUIDType):
    result = crud_delete_raffle(db, raffle_id)
    if not result:
        raise ApiError(404, ErrorCode.RAFFLE_NOT_FOUND, "Rifa no encontrada", context={"raffle_id": str(raffle_id)})
    return {"message": "Rifa eliminada con éxito"}


def update_raffle_endpoint(db: Session, raffle_id: UUIDType, data: RaffleUpdate):
    raffle = crud_update_raffle(db, raffle_id, data)
    if not raffle:
        raise ApiError(404, ErrorCode.RAFFLE_NOT_FOUND, "Rifa no encontrada", context={"raffle_id": str(raffle_id)})
    return {"message": "Rifa actualizada con éxito", "raffle": {"id": raffle.id, "title": raffle.title}}
