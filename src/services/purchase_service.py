import logging
import random
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.core.timezone import now_caracas
from src.core.errors import ApiError, ErrorCode
from src.schemas.purchase_schema import (
    PurchaseCreate,
    PurchaseResponse,
    PurchaseConfirmResponse,
    PublicPurchaseResponse,
)
from typing import List
from uuid import UUID
from src.models.purchasesModel import Purchase
from src.crud.purchase_crud import (
    crud_get_all_purchases,
    crud_get_purchase_by_id,
    crud_confirm_purchase,
    crud_get_purchase_by_ticket_number,
    crud_get_recent_or_unconfirmed_purchases,  
    crud_get_ticket_numbers_by_email,
    crud_decline_purchase
)
from src.crud.raffle_crud import (
    get_raffle_by_id,
    get_raffle_for_update,
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

logger = logging.getLogger("patealaperola")

# Validación server-side del comprobante: el frontend ya valida esto, pero
# la API nunca debe confiar en que la petición vino de ese frontend.
ALLOWED_RECEIPT_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_RECEIPT_SIZE_BYTES = 5 * 1024 * 1024  # 5MB

# Espacio de numeración cuando la rifa no define total_tickets (dato heredado).
# 10.000 = boletos de 4 dígitos, 0000–9999.
DEFAULT_TOTAL_TICKETS = 10_000


async def _read_and_validate_receipt(file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED_RECEIPT_CONTENT_TYPES:
        # 415, no 400: el payload en sí es válido, es el TIPO de archivo lo
        # que el servidor no soporta.
        raise ApiError(
            415,
            ErrorCode.INVALID_FILE_TYPE,
            "Tipo de archivo no permitido. Solo PDF, JPG o PNG.",
            context={"content_type": file.content_type, "allowed": sorted(ALLOWED_RECEIPT_CONTENT_TYPES)},
        )
    file_bytes = await file.read()
    if len(file_bytes) > MAX_RECEIPT_SIZE_BYTES:
        raise ApiError(
            413,
            ErrorCode.FILE_TOO_LARGE,
            "Archivo demasiado grande, máximo 5MB.",
            context={"max_bytes": MAX_RECEIPT_SIZE_BYTES, "received_bytes": len(file_bytes)},
        )
    return file_bytes


async def _send_email_safely(message: EmailMessage) -> None:
    # Si el correo falla, la compra ya fue confirmada/rechazada en BD: no
    # queremos que ese error rompa la respuesta ni deje al admin sin
    # confirmación de que la acción sí se aplicó.
    try:
        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=EMAIL_ADDRESS,
            password=EMAIL_PASSWORD,
        )
    except Exception:
        logger.exception("No se pudo enviar el correo de notificación al comprador")


#######################################

def get_ticket_numbers_by_email(db: Session, email: str) -> list[int]:
    return crud_get_ticket_numbers_by_email(db, email)


#############################################








def get_recent_or_unconfirmed_purchases(db: Session) -> List[PurchaseResponse]:
    purchases = crud_get_recent_or_unconfirmed_purchases(db)
    return [
        PurchaseResponse.model_validate(purchase)
        for purchase in purchases
    ]



def get_all_purchases_with_details(db: Session) -> List[PurchaseResponse]:
    purchases = crud_get_all_purchases(db)
    purchases_response = []
    for p in purchases:
        raffle = get_raffle_by_id(db, p.raffle_id)
        purchases_response.append(
            PurchaseResponse(
                id=p.id,
                raffle_id=p.raffle_id,
                raffle_title=raffle.title if raffle else None,  # antes quedaba siempre None
                buyer_email=p.buyer_email,
                ticket_numbers=p.ticket_numbers,
                total_paid=p.total_paid,
                payment_method=p.payment_method,
                payment_reference=p.payment_reference,
                purchase_date=p.purchase_date,
                full_name=p.full_name,
                phone_number=p.phone_number,
                holder_cta_bank=p.holder_cta_bank,
                is_confirmed=p.is_confirmed,
                image_url=p.image_url,
                confirmed_at=p.confirmed_at, 
                confirmed_by=p.confirmed_by 
                
            )
        )
    return purchases_response


def get_purchase_by_id(db: Session, purchase_id: UUID) -> PurchaseResponse:
    purchase = crud_get_purchase_by_id(db, purchase_id)
    if not purchase:
        raise ApiError(404, ErrorCode.PURCHASE_NOT_FOUND, "Compra no encontrada", context={"purchase_id": str(purchase_id)})

    raffle = get_raffle_by_id(db, purchase.raffle_id)  # Obtener la rifa para info adicional

    return PurchaseResponse(
        id=purchase.id,
        raffle_id=purchase.raffle_id,
        raffle_title=raffle.title,
        buyer_email=purchase.buyer_email,
        ticket_numbers=purchase.ticket_numbers,
        total_paid=purchase.total_paid,
        payment_method=purchase.payment_method,
        payment_reference=purchase.payment_reference,
        purchase_date=purchase.purchase_date,
        full_name=purchase.full_name,
        phone_number=purchase.phone_number,
        holder_cta_bank=purchase.holder_cta_bank,
        is_confirmed=purchase.is_confirmed,
        image_url=purchase.image_url, 
        confirmed_at=purchase.confirmed_at, 
        confirmed_by=purchase.confirmed_by 
    )
    
########################################

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
        <div class="info"><span class="highlight">Referencia:</span> {purchase.payment_reference}</div>
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

    await _send_email_safely(message)

    return PurchaseConfirmResponse(
        id=purchase.id,
        raffle_id=purchase.raffle_id,
        raffle_title=raffle.title if raffle else "",
        buyer_email=purchase.buyer_email,
        ticket_numbers=purchase.ticket_numbers,
        total_paid=purchase.total_paid,
        payment_method=purchase.payment_method,
        payment_reference=purchase.payment_reference,
        purchase_date=purchase.purchase_date,
        full_name=purchase.full_name,
        phone_number=purchase.phone_number,
        holder_cta_bank=purchase.holder_cta_bank,
        is_confirmed=purchase.is_confirmed,
        confirmed_at=purchase.confirmed_at,      # <-- agregado
        confirmed_by=purchase.confirmed_by
    )


async def put_decline_purchase_service(db: Session, purchase_id: UUID, decline_by: str) -> PurchaseConfirmResponse:
    purchase = crud_decline_purchase(db, purchase_id, decline_by)
    raffle = get_raffle_by_id(db, purchase.raffle_id)
    
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
        color: #c0392b;
        font-size: 24px;
        margin-bottom: 20px;
        text-align: center;
    }}
    .info {{
        font-size: 16px;
        margin-bottom: 10px;
    }}
    .highlight {{
        font-weight: bold;
        color: #34495e;
    }}
    .message {{
        font-size: 16px;
        margin: 20px 0;
        line-height: 1.6;
        color: #555;
    }}
    .footer {{
        margin-top: 30px;
        font-size: 14px;
        color: #888;
        text-align: center;
    }}
    </style>
</head>
<body>
<div class="card">
    <div class="title">❌ Su compra ha sido rechazada</div>
    <div class="info"><span class="highlight">Rifa : </span> {raffle.title if raffle else "Desconocida"}</div>
    <div class="info"><span class="highlight">Nombre:</span> {purchase.full_name}</div>
    <div class="info"><span class="highlight">Email:</span> {purchase.buyer_email}</div>
    <div class="info"><span class="highlight">Teléfono:</span> {purchase.phone_number}</div>
    <div class="message">
        Lamentamos informarle que su compra ha sido <strong>rechazada</strong> por los directivos de 
        <strong>Patea la Perola</strong>. <br><br>
        Le recomendamos ponerse en contacto con nuestro equipo de soporte a la brevedad para validar 
        las razones de este rechazo o confirmar si se trató de un error administrativo. <br><br>
        Nuestro equipo estará encantado de asistirle y brindarle la mejor solución posible.
    </div>
    <div class="footer">
        Atentamente,<br>
        <strong>Patea la Perola</strong><br>
        Equipo de Atención al Cliente
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

    await _send_email_safely(message)

    return PurchaseConfirmResponse(
        id=purchase.id,
        raffle_id=purchase.raffle_id,
        raffle_title=raffle.title if raffle else "",
        buyer_email=purchase.buyer_email,
        ticket_numbers=purchase.ticket_numbers,
        total_paid=purchase.total_paid,
        payment_method=purchase.payment_method,
        payment_reference=purchase.payment_reference,
        purchase_date=purchase.purchase_date,
        full_name=purchase.full_name,
        phone_number=purchase.phone_number,
        holder_cta_bank=purchase.holder_cta_bank,
        is_confirmed=purchase.is_confirmed,
        confirmed_at=purchase.confirmed_at,      # <-- agregado
        confirmed_by=purchase.confirmed_by
    )

##########################################################

async def create_purchase(db: Session, purchase_data: PurchaseCreate, file: UploadFile = None) -> PurchaseResponse:
    """Reserva boletos de forma atómica y registra la compra.

    Toda la reserva (leer vendidos -> elegir números -> insertar compra ->
    actualizar la rifa) ocurre dentro de UNA transacción que sostiene un lock
    de fila sobre la rifa. Antes esto eran tres transacciones separadas sin
    lock, así que dos compras simultáneas podían recibir los mismos números.
    """
    # --- 1. Validaciones baratas, sin lock -------------------------------
    raffle = get_raffle_by_id(db, purchase_data.raffle_id)
    if not raffle:
        raise ApiError(404, ErrorCode.RAFFLE_NOT_FOUND, "Rifa no encontrada", context={"raffle_id": str(purchase_data.raffle_id)})

    if raffle.raffle_status != 1:
        # 409, no 400: la rifa existe y el payload es válido, el conflicto es
        # el ESTADO actual del recurso (no está activa para comprar).
        raise ApiError(409, ErrorCode.RAFFLE_NOT_ACTIVE, "Esta rifa no está activa.")

    if purchase_data.ticket_count <= 0:
        raise ApiError(
            400,
            ErrorCode.INVALID_TICKET_COUNT,
            "La cantidad de boletos debe ser mayor a cero.",
            context={"ticket_count": purchase_data.ticket_count},
        )

    if purchase_data.ticket_count < raffle.min_purchase:
        raise ApiError(
            400,
            ErrorCode.MIN_PURCHASE_NOT_MET,
            f"Debe comprar al menos {int(raffle.min_purchase)} boletos.",
            context={"min_purchase": int(raffle.min_purchase), "ticket_count": purchase_data.ticket_count},
        )

    # --- 2. I/O de red FUERA de la transacción con lock ------------------
    # Validar y subir el comprobante puede tardar segundos; hacerlo mientras
    # se sostiene el lock bloquearía a todos los demás compradores.
    file_bytes = await _read_and_validate_receipt(file)
    db.rollback()  # cierra la transacción de sólo lectura antes del upload
    image_url = upload_file_to_gcs(file_bytes, file.filename)

    # --- 3. Reserva atómica ----------------------------------------------
    try:
        locked_raffle = get_raffle_for_update(db, purchase_data.raffle_id)
        if not locked_raffle:
            raise ApiError(404, ErrorCode.RAFFLE_NOT_FOUND, "Rifa no encontrada", context={"raffle_id": str(purchase_data.raffle_id)})

        total_tickets = locked_raffle.total_tickets or DEFAULT_TOTAL_TICKETS
        sold = {int(t) for t in (locked_raffle.tickets_sold_list or [])}
        available_numbers = set(range(0, total_tickets)) - sold

        if len(available_numbers) < purchase_data.ticket_count:
            # 409: conflicto por agotamiento de un recurso compartido (otros
            # compradores se llevaron los boletos entre que el usuario abrió
            # el formulario y envió la compra), no un payload inválido.
            raise ApiError(
                409,
                ErrorCode.INSUFFICIENT_TICKETS,
                f"Solo quedan {len(available_numbers)} boletos disponibles.",
                context={"available": len(available_numbers), "requested": purchase_data.ticket_count},
            )

        selected_numbers = sorted(
            random.sample(sorted(available_numbers), purchase_data.ticket_count)
        )

        purchase = Purchase(
            raffle_id=locked_raffle.id,
            ticket_numbers=selected_numbers,
            total_paid=purchase_data.ticket_count * locked_raffle.ticket_price,
            payment_method=purchase_data.payment_method,
            payment_reference=purchase_data.payment_reference,
            purchase_date=now_caracas(),
            buyer_email=purchase_data.buyer_email,
            full_name=purchase_data.full_name,
            phone_number=purchase_data.phone_number,
            holder_cta_bank=purchase_data.holder_cta_bank,
            image_url=image_url,
            is_confirmed=None,  # pendiente de aprobación del admin
        )
        db.add(purchase)
        locked_raffle.tickets_sold_list = sorted(sold | set(selected_numbers))

        db.commit()  # compra + boletos vendidos se guardan juntos o no se guarda nada
        db.refresh(purchase)
    except HTTPException:
        # ApiError es subclase de HTTPException (ver src/core/errors.py), así
        # que esto también atrapa el 409 de arriba: solo hace rollback y
        # re-lanza tal cual, sin tocar el código/mensaje ya armado.
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Fallo al reservar boletos para la rifa %s", purchase_data.raffle_id)
        raise

    return PurchaseResponse(
        id=purchase.id,
        raffle_id=purchase.raffle_id,
        raffle_title=raffle.title,
        buyer_email=purchase.buyer_email,
        ticket_numbers=purchase.ticket_numbers,
        total_paid=purchase.total_paid,
        payment_method=purchase.payment_method,
        payment_reference=purchase.payment_reference,
        purchase_date=purchase.purchase_date,
        full_name=purchase.full_name,
        phone_number=purchase.phone_number,
        holder_cta_bank=purchase.holder_cta_bank,
        is_confirmed=purchase.is_confirmed,
        image_url=purchase.image_url,
    )


def get_purchase_by_ticket_number(db: Session, ticket_number: int) -> PublicPurchaseResponse:
    # Endpoint público (sin login): solo se devuelven campos no sensibles.
    purchase = crud_get_purchase_by_ticket_number(db, ticket_number)
    if not purchase:
        raise ApiError(404, ErrorCode.PURCHASE_NOT_FOUND, "Compra con ese número no encontrada", context={"ticket_number": ticket_number})

    raffle = get_raffle_by_id(db, purchase.raffle_id)
    raffle_title = raffle.title if raffle else ""

    return PublicPurchaseResponse(
        id=purchase.id,
        raffle_id=purchase.raffle_id,
        raffle_title=raffle_title,
        ticket_numbers=purchase.ticket_numbers,
        purchase_date=purchase.purchase_date,
        is_confirmed=purchase.is_confirmed,
    )
