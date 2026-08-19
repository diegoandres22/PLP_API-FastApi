from fastapi import APIRouter, Depends, Query, Request, UploadFile, File, Form
from pydantic import ValidationError
from sqlalchemy.orm import Session
from src.db.deps import get_db
from src.schemas.purchase_schema import (
    PurchaseCreate,
    PurchaseResponse,
    PublicPurchaseResponse,
    TicketsByRaffleResponse,
)
from src.services import purchase_service
from uuid import UUID
from src.services.purchase_service import (
    confirm_purchase_service,
    get_purchase_by_ticket_number,
    get_ticket_numbers_by_email,
    put_decline_purchase_service,
)
from src.core.errors import ApiError, ErrorCode, error_response
from src.core.security import get_current_admin, AdminClaims
from src.core.limiter import limiter

from src.schemas.purchase_schema import PurchaseConfirmResponse
from typing import List

router = APIRouter()

# Responses comunes reutilizadas entre varios endpoints, para no repetir el
# mismo dict de documentación 5 veces.
_ADMIN_RESPONSES = {
    401: error_response(ErrorCode.UNAUTHENTICATED, "No autenticado"),
    403: error_response(ErrorCode.FORBIDDEN, "No autorizado (el token no tiene rol admin)"),
}
_PURCHASE_NOT_FOUND_RESPONSE = {
    404: error_response(ErrorCode.PURCHASE_NOT_FOUND, "Compra no encontrada", {"purchase_id": "..."}),
}


# ---- Endpoints públicos (comprador anónimo) ----------------------------
# Todos con rate limiting: son la superficie más expuesta a abuso/scraping.

@router.get(
    "/tickets-by-email/",
    response_model=List[TicketsByRaffleResponse],
    responses={429: error_response(ErrorCode.RATE_LIMITED, "Demasiadas solicitudes")},
)
@limiter.limit("10/minute")
def get_tickets_by_email(
    request: Request,
    email: str = Query(..., description="Correo del comprador"),
    db: Session = Depends(get_db),
):
    return get_ticket_numbers_by_email(db, email)


@router.get(
    "/by-ticket-number",
    response_model=PublicPurchaseResponse,
    responses={
        404: error_response(ErrorCode.PURCHASE_NOT_FOUND, "Compra con ese número no encontrada", {"ticket_number": 123}),
        429: error_response(ErrorCode.RATE_LIMITED, "Demasiadas solicitudes"),
    },
)
@limiter.limit("20/minute")
def get_purchase_by_ticket_number_endpoint(
    request: Request,
    ticket_number: int = Query(..., ge=0, le=9999),
    db: Session = Depends(get_db),
):
    # Respuesta recortada: no expone email/teléfono/referencia de pago del
    # comprador a cualquiera que adivine un número de ticket.
    return purchase_service.get_purchase_by_ticket_number(db, ticket_number)


@router.post(
    "/",
    response_model=PurchaseResponse,
    responses={
        404: error_response(ErrorCode.RAFFLE_NOT_FOUND, "Rifa no encontrada", {"raffle_id": "..."}),
        409: error_response(ErrorCode.RAFFLE_NOT_ACTIVE, "Esta rifa no está activa."),
        413: error_response(ErrorCode.FILE_TOO_LARGE, "Archivo demasiado grande, máximo 5MB."),
        415: error_response(ErrorCode.INVALID_FILE_TYPE, "Tipo de archivo no permitido. Solo PDF, JPG o PNG."),
        422: error_response(ErrorCode.VALIDATION_ERROR, "Error de validación en 1 campo(s).", {"fields": [{"field": "buyer_email", "message": "...", "type": "..."}]}),
        429: error_response(ErrorCode.RATE_LIMITED, "Demasiadas solicitudes"),
    },
)
@limiter.limit("6/minute")
async def create_purchase_route(
    request: Request,
    buyer_email: str = Form(...),
    raffle_id: UUID = Form(...),
    ticket_count: int = Form(...),
    payment_method: str = Form(...),
    payment_reference: str = Form(...),
    full_name: str = Form(...),
    phone_number: str = Form(...),
    holder_cta_bank: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        # PurchaseCreate se construye a mano porque el body es multipart/
        # form-data (necesario por el archivo adjunto), no JSON — FastAPI
        # solo valida automáticamente cuando el modelo Pydantic ES el
        # parámetro del endpoint. Antes, un pydantic.ValidationError lanzado
        # aquí (ej. buyer_email inválido) NO era un RequestValidationError,
        # así que no pasaba por el handler de 422: subía como excepción no
        # controlada y terminaba en 500. Ahora se convierte explícitamente
        # al mismo formato 422 que usa el resto de la API.
        purchase_data = PurchaseCreate(
            buyer_email=buyer_email,
            raffle_id=raffle_id,
            ticket_count=ticket_count,
            payment_method=payment_method,
            payment_reference=payment_reference,
            full_name=full_name,
            phone_number=phone_number,
            holder_cta_bank=holder_cta_bank,
        )
    except ValidationError as exc:
        fields = [
            {"field": ".".join(str(p) for p in err["loc"]), "message": err["msg"], "type": err["type"]}
            for err in exc.errors()
        ]
        raise ApiError(
            422,
            ErrorCode.VALIDATION_ERROR,
            f"Error de validación en {len(fields)} campo(s).",
            context={"fields": fields},
        )

    return await purchase_service.create_purchase(db, purchase_data, file)


# ---- Endpoints de administración (requieren JWT de admin) --------------

@router.get(
    "/confirm_Purchases",
    response_model=List[PurchaseResponse],
    responses={**_ADMIN_RESPONSES},
)
def get_pending_or_recent_purchases(
    db: Session = Depends(get_db),
    admin: AdminClaims = Depends(get_current_admin),
):
    return purchase_service.get_recent_or_unconfirmed_purchases(db)


@router.put(
    "/confirm/{purchase_id}",
    response_model=PurchaseConfirmResponse,
    responses={
        **_ADMIN_RESPONSES,
        **_PURCHASE_NOT_FOUND_RESPONSE,
        409: error_response(ErrorCode.PURCHASE_ALREADY_CONFIRMED, "La compra ya está confirmada."),
    },
)
async def confirm_purchase_endpoint(
    purchase_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminClaims = Depends(get_current_admin),
):
    # confirmed_by ya no viene del cliente: se toma del token verificado.
    return await confirm_purchase_service(db, purchase_id, admin.email)


@router.put(
    "/decline/{purchase_id}",
    response_model=PurchaseConfirmResponse,
    responses={
        **_ADMIN_RESPONSES,
        **_PURCHASE_NOT_FOUND_RESPONSE,
        409: error_response(ErrorCode.PURCHASE_ALREADY_DECLINED, "La compra ya está rechazada."),
    },
)
async def decline_purchase_endpoint(
    purchase_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminClaims = Depends(get_current_admin),
):
    return await put_decline_purchase_service(db, purchase_id, admin.email)


@router.get(
    "/all/",
    response_model=List[PurchaseResponse],
    responses={**_ADMIN_RESPONSES},
)
def get_purchases(
    db: Session = Depends(get_db),
    admin: AdminClaims = Depends(get_current_admin),
):
    return purchase_service.get_all_purchases_with_details(db)


@router.get(
    "/{purchase_id}",
    response_model=PurchaseResponse,
    responses={**_ADMIN_RESPONSES, **_PURCHASE_NOT_FOUND_RESPONSE},
)
def read_purchase(
    purchase_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminClaims = Depends(get_current_admin),
):
    return purchase_service.get_purchase_by_id(db, purchase_id)
