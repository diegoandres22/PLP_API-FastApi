from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from src.models.bank_account_model import BankAccount
from src.schemas.bank_account_schema import BankAccountCreate, BankAccountResponse, ToggleActiveResponse
from src.crud.bank_account_crud import (
    get_all_bank_accounts,
    get_bank_account_by_id,
    create_bank_account,
    toggle_bank_account_active
)

def list_bank_accounts(db: Session) -> list[BankAccountResponse]:
    accounts = get_all_bank_accounts(db)
    return [BankAccountResponse.from_orm(acc) for acc in accounts]

def create_new_bank_account(db: Session, bank_account_data: BankAccountCreate) -> BankAccountResponse:
    bank_account = BankAccount(
    pay_method=bank_account_data.pay_method,          
    holder_name_cta=bank_account_data.holder_name_cta,
    document_name=bank_account_data.document_name,
    number_cta_1=bank_account_data.number_cta_1,
    number_cta_2=bank_account_data.number_cta_2,
    email_cta=bank_account_data.email_cta,
    is_active=False
)
    created_account = create_bank_account(db, bank_account)
    return BankAccountResponse.from_orm(created_account)

def toggle_bank_account(db: Session, bank_account_id: UUID) -> ToggleActiveResponse:
    account = toggle_bank_account_active(db, bank_account_id)
    estado = "Activo" if account.is_active else "Oculto"
    message = f"El método de pago {account.pay_method} ha cambiado a {estado}"
    return ToggleActiveResponse(id=account.id, message=message)
