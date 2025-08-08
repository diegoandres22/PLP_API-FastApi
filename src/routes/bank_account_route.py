from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from src.db.deps import get_db
from src.schemas.bank_account_schema import BankAccountCreate, BankAccountResponse, ToggleActiveResponse
from src.services import bank_account_service

router = APIRouter()

@router.get("/", response_model=list[BankAccountResponse])
def get_bank_accounts(db: Session = Depends(get_db)):
    return bank_account_service.list_bank_accounts(db)

@router.post("/", response_model=BankAccountResponse)
def create_bank_account_route(bank_account: BankAccountCreate, db: Session = Depends(get_db)):
    return bank_account_service.create_new_bank_account(db, bank_account)

@router.patch("/{bank_account_id}/toggle", response_model=ToggleActiveResponse)
def toggle_bank_account_route(bank_account_id: UUID, db: Session = Depends(get_db)):
    return bank_account_service.toggle_bank_account(db, bank_account_id)
