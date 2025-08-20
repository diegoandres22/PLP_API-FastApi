
from sqlalchemy.orm import Session
from src.models.purchasesModel import Purchase
from uuid import UUID
from src.schemas.purchase_schema import PurchaseCreate, PurchaseConfirmResponse
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, any_
from typing import List

#######################

def crud_get_recent_or_unconfirmed_purchases(db: Session) -> List[Purchase]:
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    return (
        db.query(Purchase)
        .filter(
            or_(
                Purchase.is_confirmed == False,
                Purchase.is_confirmed == None,
                and_(
                    Purchase.is_confirmed == True,
                    Purchase.confirmed_at >= one_day_ago
                )
            )
        )
        .order_by(Purchase.purchase_date.desc())
        .all()
    )
#######################

















def crud_get_purchase_by_id(db: Session, purchase_id: UUID) -> Purchase | None:
    return db.query(Purchase).filter(Purchase.id == purchase_id).first()

def crud_get_all_purchases(db: Session) -> list[Purchase]:
    return db.query(Purchase).all()

def crud_create_purchase(db: Session, purchase: Purchase) -> Purchase:
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase


def crud_confirm_purchase(db: Session, purchase_id: UUID, confirmed_by: str) -> Purchase:
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    if purchase.is_confirmed:
        raise HTTPException(status_code=400, detail="La compra ya está confirmada")
    
    purchase.is_confirmed = True
    utc_now = datetime.utcnow()
    purchase.confirmed_at = utc_now - timedelta(hours=4)
    purchase.confirmed_by = confirmed_by
    db.commit()
    db.refresh(purchase)

    return purchase


def crud_get_purchase_by_ticket_number(db: Session, ticket_number: int) -> Purchase | None:
    return db.query(Purchase).filter(ticket_number == any_(Purchase.ticket_numbers)).first()

