import random
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.raffleModel import Raffle
from src.schemas.purchase_schema import PurchaseCreate, PurchaseResponse
from typing import List 
from uuid import UUID
from src.models.purchasesModel import Purchase
from src.crud.purchase_crud import (
    crud_get_all_purchases,
    crud_get_purchase_by_id,
    crud_create_purchase
)
from src.crud.raffle_crud import (
    get_raffle_by_id, update_raffle_tickets_sold
)

def get_all_purchases(db: Session):
    return crud_get_all_purchases(db)


def get_purchase_by_id(db: Session, purchase_id: UUID) -> PurchaseResponse:
    purchase = crud_get_purchase_by_id(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return PurchaseResponse(
        id=purchase.id,
        tickets=purchase.ticket_numbers,
        email=purchase.buyer_email,
        raffle=purchase.raffle_id,
        purchase_date=purchase.purchase_date
    )

def create_purchase(db: Session, purchase_data: PurchaseCreate) -> PurchaseResponse:
    # Buscar la rifa por ID
    raffle = get_raffle_by_id(db, purchase_data.raffle_id)
    if not raffle:
        raise HTTPException(status_code=404, detail="Rifa no encontrada")

    # Verificar compra mínima
    if purchase_data.ticket_count < raffle.min_purchase:
        raise HTTPException(status_code=400, detail=f"Debe comprar al menos {raffle.min_purchase} boletos")

    # Calcular boletos disponibles
    tickets_left = raffle.total_tickets - raffle.tickets_sold
    if purchase_data.ticket_count > tickets_left:
        raise HTTPException(status_code=400, detail="No hay suficientes tickets disponibles")

    # Asignar números de tickets aleatorios sin validar duplicados para simplificar (puedes mejorar luego)
    selected_numbers = random.sample(range(1, raffle.total_tickets + 1), purchase_data.ticket_count)

    # Crear compra
    new_purchase = Purchase(
        raffle_id=raffle.id,  
        ticket_numbers=selected_numbers,
        total_paid=purchase_data.ticket_count * raffle.ticket_price,
        payment_method=purchase_data.payment_method,
        payment_ref=purchase_data.payment_reference,
        purchase_date=datetime.utcnow(),
        buyer_email=purchase_data.email  
    )
    # Guarda la compra
    purchase = crud_create_purchase(db, new_purchase)
    
    # Actualiza la rifa
    update_raffle_tickets_sold(db, raffle, purchase_data.ticket_count)

    # Retornar respuesta 
    return PurchaseResponse(
    id=new_purchase.id,
    raffle_id=raffle.id,
    raffle_title=raffle.title,
    email=purchase_data.email,
    ticket_numbers=selected_numbers,
    total_paid=purchase_data.ticket_count * raffle.ticket_price,
    payment_method=purchase_data.payment_method,
    payment_ref=purchase_data.payment_reference,
    purchase_date=new_purchase.purchase_date
)
