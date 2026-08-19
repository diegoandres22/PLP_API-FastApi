from fastapi import APIRouter, Depends, Form, File, UploadFile
from pydantic import ValidationError
from sqlalchemy.orm import Session
from src.db.deps import get_db
from src.services import raffle_service
from src.schemas.raffle_schema import RaffleCreate, RaffleUpdate
from uuid import UUID
from datetime import datetime
from src.services.gcs_service import upload_file_to_gcs
from src.core.errors import ApiError, ErrorCode, error_response
from src.core.security import get_current_admin, AdminClaims


router = APIRouter()

_ADMIN_RESPONSES = {
    401: error_response(ErrorCode.UNAUTHENTICATED, "No autenticado"),
    403: error_response(ErrorCode.FORBIDDEN, "No autorizado (el token no tiene rol admin)"),
}
_RAFFLE_NOT_FOUND_RESPONSE = {
    404: error_response(ErrorCode.RAFFLE_NOT_FOUND, "Rifa no encontrada", {"raffle_id": "..."}),
}

# Lectura: pública, cualquier visitante navega las rifas.
@router.get("/all/")
def get_all_raffles(db: Session = Depends(get_db)):
    return raffle_service.get_raffles_endpoint(db)


@router.get("/{raffle_id}", responses={**_RAFFLE_NOT_FOUND_RESPONSE})
def get_raffle_by_id(raffle_id: UUID, db: Session = Depends(get_db)):
    return raffle_service.get_raffle_by_id_endpoint(db, raffle_id)


# A partir de aquí: solo administradores autenticados (JWT del panel admin).
@router.post(
    "/new/",
    responses={
        **_ADMIN_RESPONSES,
        422: error_response(ErrorCode.VALIDATION_ERROR, "Error de validación en 1 campo(s).", {"fields": [{"field": "ticket_price", "message": "...", "type": "..."}]}),
    },
)
async def create_raffle_endpoint(
    title: str = Form(...),
    description: str = Form(...),
    ticket_price: float = Form(...),
    min_purchase: float = Form(...),
    raffle_status: int = Form(...),
    state: bool = Form(...),
    trophy: str = Form(...),
    secondPrize: str = Form(...),
    additionalPrize: str = Form(...),
    premium_ticket1: int = Form(None),
    premium_ticket2: int = Form(None),
    premium_ticket3: int = Form(None),
    premium_ticket4: int = Form(None),
    premium_ticket5: int = Form(None),
    premium_ticket6: int = Form(None),
    total_tickets: int = Form(...),
    lottery_date: datetime = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminClaims = Depends(get_current_admin),
):
    file_bytes = await file.read()
    image_url = upload_file_to_gcs(file_bytes, file.filename)

    try:
        # Mismo caso que PurchaseCreate en purchase_router.py: RaffleCreate
        # se construye a mano porque el body es multipart/form-data (por el
        # archivo del premio), así que FastAPI no lo valida automáticamente.
        # Sin este try/except, un ValidationError aquí subía como 500 en vez
        # de 422.
        raffle_data = RaffleCreate(
            title=title,
            description=description,
            ticket_price=ticket_price,
            min_purchase=min_purchase,
            raffle_status=raffle_status,
            state=state,
            trophy=trophy,
            secondPrize=secondPrize,
            additionalPrize=additionalPrize,
            premium_ticket1=premium_ticket1,
            premium_ticket2=premium_ticket2,
            premium_ticket3=premium_ticket3,
            premium_ticket4=premium_ticket4,
            premium_ticket5=premium_ticket5,
            premium_ticket6=premium_ticket6,
            total_tickets=total_tickets,
            lottery_date=lottery_date,
            created_by=admin.email,  # nunca se confía en un campo enviado por el cliente para esto
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

    return raffle_service.create_raffle(raffle_data, db, image_url)


@router.delete("/{raffle_id}", responses={**_ADMIN_RESPONSES, **_RAFFLE_NOT_FOUND_RESPONSE})
def delete_raffle(
    raffle_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminClaims = Depends(get_current_admin),
):
    return raffle_service.delete_raffle_endpoint(db, raffle_id)


@router.put("/{raffle_id}", responses={**_ADMIN_RESPONSES, **_RAFFLE_NOT_FOUND_RESPONSE})
def update_raffle(
    raffle_id: UUID,
    data: RaffleUpdate,
    db: Session = Depends(get_db),
    admin: AdminClaims = Depends(get_current_admin),
):
    data.updated_by = admin.email
    return raffle_service.update_raffle_endpoint(db, raffle_id, data)
