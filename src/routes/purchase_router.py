from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.db.deps import get_db 
from src.schemas.purchase_schema import PurchaseCreate, PurchaseResponse
from src.services import purchase_service
from uuid import UUID
from src.models.purchasesModel import Purchase
from src.services.purchase_service import confirm_purchase_service, get_purchase_by_ticket_number
from src.schemas.purchase_schema import PurchaseConfirmResponse
from typing import List

router = APIRouter()

@router.put("/confirm/{purchase_id}", response_model=PurchaseConfirmResponse)
async def confirm_purchase_endpoint(purchase_id: UUID, confirmed_by: str, db: Session = Depends(get_db)):
    return await confirm_purchase_service(db, purchase_id, confirmed_by)



@router.get("/all/", response_model=List[PurchaseResponse])
def get_purchases(db: Session = Depends(get_db)):
    return purchase_service.get_all_purchases_with_details(db)

@router.get("/{purchase_id}", response_model=PurchaseResponse)
def read_purchase(purchase_id: UUID, db: Session = Depends(get_db)):
    return purchase_service.get_purchase_by_id(db, purchase_id)

@router.post("/", response_model=PurchaseResponse)
async def create_purchase_route(
    email: str = Form(...),
    raffle_id: UUID = Form(...),
    ticket_count: int = Form(...),
    payment_method: str = Form(...),
    payment_reference: str = Form(...),
    full_name: str = Form(...),
    phone_number: str = Form(...),
    holder_cta_bank: str = Form(...),
    file: UploadFile = File(),   # Imagen opcional
    db: Session = Depends(get_db)
):
    # Crear objeto PurchaseCreate desde los campos del formulario
    purchase_data = PurchaseCreate(
        email=email,
        raffle_id=raffle_id,
        ticket_count=ticket_count,
        payment_method=payment_method,
        payment_reference=payment_reference,
        full_name=full_name,
        phone_number=phone_number,
        holder_cta_bank=holder_cta_bank
    )
    # Llamar al servicio que maneja la creación y subida de imagen
    return await purchase_service.create_purchase(db, purchase_data, file)



@router.get("/by-ticket-number", response_model=PurchaseResponse)
def get_purchase_by_ticket_number_endpoint(
    ticket_number: int = Query(..., ge=0, le=9999),
    db: Session = Depends(get_db)
):
    
    return purchase_service.get_purchase_by_ticket_number(db, ticket_number)
