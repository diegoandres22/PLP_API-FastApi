from datetime import timedelta
from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, any_, or_
from sqlalchemy.orm import Session

from src.core.timezone import now_caracas
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
        raise HTTPException(status_code=404, detail="Compra no encontrada")

    if purchase.is_confirmed:
        raise HTTPException(status_code=400, detail="La compra ya está confirmada")

    purchase.is_confirmed = True
    purchase.confirmed_at = now_caracas()
    purchase.confirmed_by = confirmed_by
    db.commit()
    db.refresh(purchase)

    return purchase


def crud_decline_purchase(db: Session, purchase_id: UUID, decline_by: str) -> Purchase:
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Compra no encontrada")

    if purchase.is_confirmed is False:
        raise HTTPException(status_code=400, detail="La compra ya está rechazada")

    purchase.is_confirmed = False
    purchase.confirmed_at = now_caracas()
    purchase.confirmed_by = decline_by
    db.commit()
    db.refresh(purchase)

    return purchase


def crud_get_purchase_by_ticket_number(db: Session, ticket_number: int) -> Purchase | None:
    return db.query(Purchase).filter(ticket_number == any_(Purchase.ticket_numbers)).first()
