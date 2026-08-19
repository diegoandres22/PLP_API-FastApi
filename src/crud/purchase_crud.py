from datetime import timedelta
from typing import List
from uuid import UUID

from sqlalchemy import and_, any_, or_
from sqlalchemy.orm import Session

from src.core.errors import ApiError, ErrorCode
from src.core.timezone import now_caracas
from src.crud.raffle_crud import get_raffle_for_update
from src.models.purchasesModel import Purchase
from src.models.raffleModel import Raffle


def crud_get_ticket_numbers_by_email(db: Session, email: str) -> list[dict]:
    # Rifas activas
    active_raffle_ids = {
        r.id for r in db.query(Raffle.id).filter(Raffle.raffle_status == 1).all()
    }

    # Compras confirmadas del usuario dentro de esas rifas
    purchases = (
        db.query(Purchase)
        .filter(
            Purchase.buyer_email == email,
            Purchase.is_confirmed.is_(True),
            Purchase.raffle_id.in_(active_raffle_ids) if active_raffle_ids else False,
        )
        .all()
    )

    result = []
    for raffle_id in active_raffle_ids:
        raffle_tickets = [
            ticket
            for p in purchases if p.raffle_id == raffle_id
            for ticket in p.ticket_numbers
        ]
        if raffle_tickets:
            result.append({
                "raffle_id": raffle_id,
                "ticket_numbers": sorted(raffle_tickets),
            })

    return result


def crud_get_recent_or_unconfirmed_purchases(db: Session) -> List[Purchase]:
    # confirmed_at se guarda en hora de Caracas, así que el corte también
    # debe calcularse en esa zona. Con utcnow() el umbral se corría 4 horas.
    one_day_ago = now_caracas() - timedelta(days=1)

    return (
        db.query(Purchase)
        .filter(
            or_(
                # Pendientes
                Purchase.is_confirmed.is_(None),
                # Aprobadas o rechazadas recientemente
                and_(
                    Purchase.is_confirmed.isnot(None),
                    Purchase.confirmed_at.isnot(None),
                    Purchase.confirmed_at >= one_day_ago,
                ),
            )
        )
        .order_by(Purchase.purchase_date.desc())
        .all()
    )


def crud_get_purchase_by_id(db: Session, purchase_id: UUID) -> Purchase | None:
    return db.query(Purchase).filter(Purchase.id == purchase_id).first()


def crud_get_all_purchases(db: Session) -> list[Purchase]:
    return db.query(Purchase).all()


def crud_confirm_purchase(db: Session, purchase_id: UUID, confirmed_by: str) -> Purchase:
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise ApiError(404, ErrorCode.PURCHASE_NOT_FOUND, "Compra no encontrada", context={"purchase_id": str(purchase_id)})

    # Antes solo se comprobaba `is_confirmed` truthy (bloqueaba re-confirmar),
    # pero una compra YA RECHAZADA (is_confirmed is False) pasaba esta
    # comprobación sin problema y quedaba "confirmada" en silencio — sin
    # avisar que se estaba revirtiendo un rechazo. Ahora ambas transiciones
    # inválidas están bloqueadas explícitamente.
    if purchase.is_confirmed is True:
        raise ApiError(409, ErrorCode.PURCHASE_ALREADY_CONFIRMED, "La compra ya está confirmada.")
    if purchase.is_confirmed is False:
        raise ApiError(
            409,
            ErrorCode.PURCHASE_ALREADY_DECLINED,
            "La compra ya fue rechazada; no se puede confirmar.",
        )

    purchase.is_confirmed = True
    purchase.confirmed_at = now_caracas()
    purchase.confirmed_by = confirmed_by
    db.commit()
    db.refresh(purchase)

    return purchase


def crud_decline_purchase(db: Session, purchase_id: UUID, decline_by: str) -> Purchase:
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise ApiError(404, ErrorCode.PURCHASE_NOT_FOUND, "Compra no encontrada", context={"purchase_id": str(purchase_id)})

    # Mismo problema simétrico: antes solo se comprobaba `is_confirmed is
    # False` (bloqueaba re-rechazar), pero una compra YA CONFIRMADA
    # (is_confirmed is True) pasaba sin problema y quedaba "rechazada" sin
    # que los boletos que ya tenía reservados volvieran a estar disponibles
    # — es decir, esos números quedaban perdidos para siempre (ni vendidos
    # ni comprables). Ahora esa transición también está bloqueada.
    if purchase.is_confirmed is False:
        raise ApiError(409, ErrorCode.PURCHASE_ALREADY_DECLINED, "La compra ya está rechazada.")
    if purchase.is_confirmed is True:
        raise ApiError(
            409,
            ErrorCode.PURCHASE_ALREADY_CONFIRMED,
            "La compra ya fue confirmada; no se puede rechazar.",
        )

    # Con las dos guardas de arriba, solo se llega aquí si is_confirmed es
    # None (pendiente): es el único caso donde hay boletos reservados que
    # liberar. Se hace bajo el mismo lock de fila que usa create_purchase,
    # para no pisar una reserva concurrente de otro comprador.
    raffle = get_raffle_for_update(db, purchase.raffle_id)
    if raffle:
        sold = {int(t) for t in (raffle.tickets_sold_list or [])}
        released = sold - {int(t) for t in (purchase.ticket_numbers or [])}
        raffle.tickets_sold_list = sorted(released)
    # Si raffle es None, la rifa fue borrada mientras la compra seguía
    # pendiente (caso raro, ver auditoría de integridad de datos): no hay
    # tickets_sold_list a la que devolver los números, pero igual se permite
    # rechazar la compra huérfana.

    purchase.is_confirmed = False
    purchase.confirmed_at = now_caracas()
    purchase.confirmed_by = decline_by
    db.commit()
    db.refresh(purchase)

    return purchase


def crud_get_purchase_by_ticket_number(db: Session, ticket_number: int) -> Purchase | None:
    return db.query(Purchase).filter(ticket_number == any_(Purchase.ticket_numbers)).first()
