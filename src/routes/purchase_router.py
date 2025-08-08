from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.deps import get_db 
from src.schemas.purchase_schema import PurchaseCreate, PurchaseResponse
from src.services import purchase_service
from uuid import UUID
from src.models.purchasesModel import Purchase
from src.services.purchase_service import confirm_purchase_service
from src.schemas.purchase_schema import PurchaseConfirmResponse

router = APIRouter()

@router.put("/purchase/{purchase_id}/confirm", response_model=PurchaseConfirmResponse)
async def confirm_purchase_endpoint(purchase_id: UUID, db: Session = Depends(get_db)):
    return await confirm_purchase_service(db, purchase_id)

@router.put("/purchase/{purchase_id}/confirm", response_model=PurchaseConfirmResponse)
def confirm_purchase_endpoint(purchase_id: UUID, db: Session = Depends(get_db)):
    return confirm_purchase_service(db, purchase_id)

@router.get("/purchases/")
def get_purchases(db: Session = Depends(get_db)):
    purchases = db.query(Purchase).all()
    return {
        "Compras": [
            {
                "id": str(p.id),
                "ticket_numbers": p.ticket_numbers,
                "total_paid": p.total_paid,
                "payment_method": p.payment_method,
                "payment_ref": p.payment_ref,
                "purchase_date": p.purchase_date.isoformat(),
                "buyer_email": p.buyer_email,
                "raffle_id": str(p.raffle_id),
                "full_name": p.full_name,
                "phone_number": p.phone_number,
                "holder_cta_bank": p.holder_cta_bank,
                "is_confirmed": p.is_confirmed
            } for p in purchases
        ]
    }

@router.get("/purchases/{purchase_id}", response_model=PurchaseResponse)
def read_purchase(purchase_id: UUID, db: Session = Depends(get_db)):
    return purchase_service.get_purchase_by_id(db, purchase_id)



@router.post("/", response_model=PurchaseResponse)
def create_purchase_route(purchase: PurchaseCreate, db: Session = Depends(get_db)):
    return purchase_service.create_purchase(db, purchase)

