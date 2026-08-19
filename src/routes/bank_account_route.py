from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from src.db.deps import get_db
from src.schemas.bank_account_schema import BankAccountCreate, BankAccountResponse, ToggleActiveResponse
from src.services import bank_account_service
from src.core.errors import ErrorCode, error_response
from src.core.security import get_current_admin, AdminClaims

router = APIRouter()

_ADMIN_RESPONSES = {
    401: error_response(ErrorCode.UNAUTHENTICATED, "No autenticado"),
    403: error_response(ErrorCode.FORBIDDEN, "No autorizado (el token no tiene rol admin)"),
}

# Pública: el comprador necesita ver a qué cuenta transferir.
@router.get("/", response_model=list[BankAccountResponse])
def get_bank_accounts(db: Session = Depends(get_db)):
    return bank_account_service.list_bank_accounts(db)


# Administración de cuentas: requiere JWT de admin.
# No hace falta el try/except de ValidationError de los otros dos routers:
# aquí el body SÍ es JSON nativo (BankAccountCreate es el parámetro
# directamente), así que FastAPI ya valida y devuelve 422 automáticamente
# antes de que este código se ejecute.
@router.post("/", response_model=BankAccountResponse, responses={**_ADMIN_RESPONSES})
def create_bank_account_route(
    bank_account: BankAccountCreate,
    db: Session = Depends(get_db),
    admin: AdminClaims = Depends(get_current_admin),
):
    return bank_account_service.create_new_bank_account(db, bank_account)


@router.patch(
    "/{bank_account_id}/toggle",
    response_model=ToggleActiveResponse,
    responses={
        **_ADMIN_RESPONSES,
        404: error_response(ErrorCode.BANK_ACCOUNT_NOT_FOUND, "Cuenta bancaria no encontrada", {"bank_account_id": "..."}),
    },
)
def toggle_bank_account_route(
    bank_account_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminClaims = Depends(get_current_admin),
):
    return bank_account_service.toggle_bank_account(db, bank_account_id)
