
from sqlalchemy.orm import Session
from src.models.purchasesModel import Purchase
from uuid import UUID

def crud_get_purchase_by_id(db: Session, purchase_id: UUID) -> Purchase | None:
    return db.query(Purchase).filter(Purchase.id == purchase_id).first()

def crud_get_all_purchases(db: Session) -> list[Purchase]:
    return db.query(Purchase).all()

def crud_create_purchase(db: Session, purchase: Purchase) -> Purchase:
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase
