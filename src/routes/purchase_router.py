from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.deps import get_db 
from src.schemas.purchase_schema import PurchaseCreate, PurchaseResponse
from src.services import purchase_service
from uuid import UUID
from src.models.purchasesModel import Purchase


router = APIRouter()

@router.get("/purchases/")
def get_purchases(db: Session = Depends(get_db)):
    purchases = db.query(Purchase).all()
    return {
        "Purchases": [
            {
                "id": str(p.id),
                "ticket_numbers": p.ticket_numbers,
                "total_paid": p.total_paid,
                "payment_method": p.payment_method,
                "payment_ref": p.payment_ref,
                "purchase_date": p.purchase_date.isoformat(),
                "buyer_email": p.buyer_email
            } for p in purchases
        ]
    }

@router.get("/purchases/{purchase_id}", response_model=PurchaseResponse)
def read_purchase(purchase_id: UUID, db: Session = Depends(get_db)):
    return purchase_service.get_purchase_by_id(db, purchase_id)



@router.post("/", response_model=PurchaseResponse)
def create_purchase_route(purchase: PurchaseCreate, db: Session = Depends(get_db)):
    return purchase_service.create_purchase(db, purchase)

