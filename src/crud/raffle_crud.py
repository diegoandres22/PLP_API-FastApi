from uuid import UUID as UUIDType

from sqlalchemy.orm import Session

from src.models.raffleModel import Raffle
from src.schemas.raffle_schema import RaffleUpdate


# Nota: estas funciones ya NO reordenan tickets_sold_list sobre la instancia
# del ORM. Hacerlo marcaba la entidad como "sucia" y el siguiente commit
# reescribía la columna como efecto colateral de una simple lectura. El
# ordenamiento es presentación y ahora vive en la capa de servicio.

def get_all_raffles(db: Session) -> list[Raffle]:
    return db.query(Raffle).all()


def get_raffle_by_id(db: Session, raffle_id: UUIDType) -> Raffle | None:
    return db.query(Raffle).filter(Raffle.id == raffle_id).first()


def get_raffle_for_update(db: Session, raffle_id: UUIDType) -> Raffle | None:
    """Lee la rifa tomando un lock de fila (SELECT ... FOR UPDATE).

    Es la pieza que serializa la venta de boletos: mientras una transacción
    mantiene este lock, cualquier otra que intente reservar boletos de la
    MISMA rifa queda en espera, en vez de leer una lista de vendidos vieja y
    asignar los mismos números.
    """
    return (
        db.query(Raffle)
        .filter(Raffle.id == raffle_id)
        .with_for_update()
        .first()
    )


def crud_create_raffle(db: Session, data: dict) -> Raffle:
    raffle = Raffle(**data)
    db.add(raffle)
    db.commit()
    db.refresh(raffle)
    return raffle


def update_raffle(db: Session, raffle_id: UUIDType, data: RaffleUpdate) -> Raffle | None:
    raffle = get_raffle_by_id(db, raffle_id)
    if not raffle:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(raffle, key, value)
    db.commit()
    db.refresh(raffle)
    return raffle


def delete_raffle(db: Session, raffle_id: UUIDType) -> bool | None:
    raffle = get_raffle_by_id(db, raffle_id)
    if not raffle:
        return None
    db.delete(raffle)
    db.commit()
    return True
