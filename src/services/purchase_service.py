import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.schemas.purchase_schema import PurchaseCreate, PurchaseResponse, PurchaseConfirmResponse
from typing import List 
from uuid import UUID
from src.models.purchasesModel import Purchase
from src.crud.purchase_crud import (
    crud_get_all_purchases,
    crud_get_purchase_by_id,
    crud_create_purchase,
    crud_confirm_purchase,
    crud_get_purchase_by_ticket_number
)
from src.crud.raffle_crud import (
    get_raffle_by_id, update_raffle_tickets_sold
)
from fastapi import UploadFile
from email.message import EmailMessage
import aiosmtplib
import os
from dotenv import load_dotenv
load_dotenv()
from src.services.gcs_service import upload_file_to_gcs


EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def get_all_purchases_with_details(db: Session) -> List[PurchaseResponse]:
    purchases = crud_get_all_purchases(db)
    purchases_response = []
    for p in purchases:
        purchases_response.append(
            PurchaseResponse(
                id=p.id,
                raffle_id=p.raffle_id,
                raffle_title=None,  # si quieres omitir el título
                email=p.buyer_email,
                ticket_numbers=p.ticket_numbers,
                total_paid=p.total_paid,
                payment_method=p.payment_method,
                payment_ref=p.payment_ref,
                purchase_date=p.purchase_date,
                full_name=p.full_name,
                phone_number=p.phone_number,
                holder_cta_bank=p.holder_cta_bank,
                is_confirmed=p.is_confirmed,
                image_url=p.image_url
            )
        )
    return purchases_response


def get_purchase_by_id(db: Session, purchase_id: UUID) -> PurchaseResponse:
    purchase = crud_get_purchase_by_id(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Compra no encontrada")

    raffle = get_raffle_by_id(db, purchase.raffle_id)  # Obtener la rifa para info adicional

    return PurchaseResponse(
        id=purchase.id,
        raffle_id=purchase.raffle_id,
        raffle_title=raffle.title,
        email=purchase.buyer_email,
        ticket_numbers=purchase.ticket_numbers,
        total_paid=purchase.total_paid,
        payment_method=purchase.payment_method,
        payment_ref=purchase.payment_ref,
        purchase_date=purchase.purchase_date,
        full_name=purchase.full_name,
        phone_number=purchase.phone_number,
        holder_cta_bank=purchase.holder_cta_bank,
        is_confirmed=purchase.is_confirmed,
        image_url=purchase.image_url
    )
    
    
    
    


async def confirm_purchase_service(db: Session, purchase_id: UUID, confirmed_by: str) -> PurchaseConfirmResponse:
    purchase = crud_confirm_purchase(db, purchase_id, confirmed_by)
    raffle = get_raffle_by_id(db, purchase.raffle_id)
    
    ticket_numbers_str = ", ".join(str(n) for n in purchase.ticket_numbers)
    
    html_content = f"""
    <html>
    <head>
        <style>
        body {{
        font-family: 'Arial', sans-serif;
        background-color: #f4f4f4;
        padding: 20px;
        }}
        .card {{
        background-color: #ffffff;
        border-radius: 8px;
        padding: 30px;
        max-width: 600px;
        margin: auto;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .title {{
        color: #2e86de;
        font-size: 24px;
        margin-bottom: 20px;
        }}
        .info {{
        font-size: 16px;
        margin-bottom: 10px;
        }}
        .highlight {{
        font-weight: bold;
        color: #34495e;
        }}
        .footer {{
        margin-top: 20px;
        font-size: 14px;
        color: #888;
        text-align: center;
        }}
        </style>
    </head>
    <body>
    <div class="card">
        <div class="title">🎟️ Confirmación de tu compra</div>
        <div class="info"><span class="highlight">Nombre:</span> {purchase.full_name}</div>
        <div class="info"><span class="highlight">Email:</span> {purchase.buyer_email}</div>
        <div class="info"><span class="highlight">Teléfono:</span> {purchase.phone_number}</div>
        <div class="info"><span class="highlight">Boletos:</span> {ticket_numbers_str}</div>
        <div class="info"><span class="highlight">Total pagado:</span> ${purchase.total_paid}</div>
        <div class="info"><span class="highlight">Método de pago:</span> {purchase.payment_method}</div>
        <div class="info"><span class="highlight">Referencia:</span> {purchase.payment_ref}</div>
        <div class="info"><span class="highlight">Fecha:</span> {purchase.purchase_date.strftime('%Y-%m-%d %H:%M:%S')}</div>
        <div class="info"><span class="highlight">Titular de la cuenta:</span> {purchase.holder_cta_bank}</div>
        <div class="footer">
        <strong>Patea la Perola</strong>
        </div>
    </div>
    </body>
</html>
"""


    message = EmailMessage()
    message["From"] = f"Patea la perola <{EMAIL_ADDRESS}>"
    message["To"] = purchase.buyer_email
    message["Subject"] = "Confirmación de compra - Patea la perola"
    message.set_content("Tu cliente de correo no soporta HTML.")
    message.add_alternative(html_content, subtype="html")


    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=EMAIL_ADDRESS,
        password=EMAIL_PASSWORD,
    )

    return PurchaseConfirmResponse(
        id=purchase.id,
        raffle_id=purchase.raffle_id,
        raffle_title=raffle.title if raffle else "",
        buyer_email=purchase.buyer_email,
        ticket_numbers=purchase.ticket_numbers,
        total_paid=purchase.total_paid,
        payment_method=purchase.payment_method,
        payment_ref=purchase.payment_ref,
        purchase_date=purchase.purchase_date,
        full_name=purchase.full_name,
        phone_number=purchase.phone_number,
        holder_cta_bank=purchase.holder_cta_bank,
        is_confirmed=purchase.is_confirmed,
        confirmed_at=purchase.confirmed_at,      # <-- agregado
        confirmed_by=purchase.confirmed_by  
    )
    
    














async def create_purchase(db: Session, purchase_data: PurchaseCreate,  file: UploadFile = None) -> PurchaseResponse:
    # Buscar la rifa
    raffle = get_raffle_by_id(db, purchase_data.raffle_id)
    if not raffle:
        raise HTTPException(status_code=404, detail="Rifa no encontrada")

    # Validar compra mínima
    if purchase_data.ticket_count < raffle.min_purchase:
        raise HTTPException(status_code=400, detail=f"Debe comprar al menos {raffle.min_purchase} boletos")

    # Inicializar lista de boletos vendidos
    sold = set(raffle.tickets_sold_list or [])
    total_available = 9999

    # Validar disponibilidad de boletos
    if len(sold) + purchase_data.ticket_count > total_available:
        raise HTTPException(status_code=400, detail="No hay suficientes boletos disponibles")

    # Generar boletos únicos
    available_numbers = set(f"{i:04d}" for i in range(0, total_available)) - sold
    selected_numbers = random.sample(list(available_numbers), purchase_data.ticket_count)

    # Subir la imagen si existe
    
    file_bytes = await file.read()
    image_url = upload_file_to_gcs(file_bytes, file.filename)

    # Crear nueva compra
    purchase = Purchase(
    raffle_id=raffle.id,
    ticket_numbers=selected_numbers,
    total_paid=purchase_data.ticket_count * raffle.ticket_price,
    payment_method=purchase_data.payment_method,
    payment_ref=purchase_data.payment_reference,
    purchase_date=datetime.utcnow() - timedelta(hours=4),  # Restar 4 horas manualmente para hora Caracas
    buyer_email=purchase_data.email,
    full_name=purchase_data.full_name,
    phone_number=purchase_data.phone_number,
    holder_cta_bank=purchase_data.holder_cta_bank,
    image_url=image_url, #imagen de la compra
    is_confirmed=False  # Inicialmente no confirmado
)
    purchase = crud_create_purchase(db, purchase)

    # Actualizar boletos vendidos en la rifa
    updated_sold = list(sold.union(set(selected_numbers)))
    update_raffle_tickets_sold(db, raffle, updated_sold)

    # Respuesta
    return PurchaseResponse(
    id=purchase.id,
    raffle_id=raffle.id,
    email=purchase_data.email,
    ticket_numbers=selected_numbers,
    total_paid=purchase.total_paid,
    payment_method=purchase.payment_method,
    payment_ref=purchase.payment_ref,
    purchase_date=purchase.purchase_date,
    full_name=purchase_data.full_name,
    phone_number=purchase_data.phone_number,
    holder_cta_bank=purchase_data.holder_cta_bank,
    is_confirmed=purchase.is_confirmed,
    image_url=image_url,
    raffle_title=raffle.title
)



def get_purchase_by_ticket_number(db: Session, ticket_number: int) -> PurchaseResponse:
    purchase = crud_get_purchase_by_ticket_number(db, ticket_number)
    if not purchase:
        raise HTTPException(status_code=404, detail="Compra con ese número no encontrada")

    raffle = get_raffle_by_id(db, purchase.raffle_id)
    raffle_title = raffle.title if raffle else ""

    return PurchaseResponse(
        id=purchase.id,
        raffle_id=purchase.raffle_id,
        raffle_title=raffle_title,
        email=purchase.buyer_email,
        ticket_numbers=purchase.ticket_numbers,
        total_paid=purchase.total_paid,
        payment_method=purchase.payment_method,
        payment_ref=purchase.payment_ref,
        purchase_date=purchase.purchase_date,
        full_name=purchase.full_name,
        phone_number=purchase.phone_number,
        holder_cta_bank=purchase.holder_cta_bank,
        is_confirmed=purchase.is_confirmed,
        image_url=purchase.image_url 

    )
