
from sqlalchemy.orm import Session
from src.models.purchasesModel import Purchase
from uuid import UUID
from src.schemas.purchase_schema import PurchaseCreate, PurchaseConfirmResponse
from fastapi import HTTPException


def crud_get_purchase_by_id(db: Session, purchase_id: UUID) -> Purchase | None:
    return db.query(Purchase).filter(Purchase.id == purchase_id).first()

def crud_get_all_purchases(db: Session) -> list[Purchase]:
    return db.query(Purchase).all()

def crud_create_purchase(db: Session, purchase: Purchase) -> Purchase:
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase


def crud_confirm_purchase(db: Session, purchase_id: UUID) -> Purchase:
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    if purchase.is_confirmed:
        raise HTTPException(status_code=400, detail="La compra ya está confirmada")
    
    purchase.is_confirmed = True
    db.commit()
    db.refresh(purchase)

    return purchase