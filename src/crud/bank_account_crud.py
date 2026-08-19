from sqlalchemy.orm import Session
from src.models.bank_account_model import BankAccount
from uuid import UUID
from src.core.errors import ApiError, ErrorCode

def get_all_bank_accounts(db: Session) -> list[BankAccount]:
    return db.query(BankAccount).all()

def get_bank_account_by_id(db: Session, bank_account_id: UUID) -> BankAccount | None:
    return db.query(BankAccount).filter(BankAccount.id == bank_account_id).first()

def create_bank_account(db: Session, bank_account: BankAccount) -> BankAccount:
    db.add(bank_account)
    db.commit()
    db.refresh(bank_account)
    return bank_account

def toggle_bank_account_active(db: Session, bank_account_id: UUID) -> BankAccount:
    bank_account = get_bank_account_by_id(db, bank_account_id)
    if not bank_account:
        raise ApiError(404, ErrorCode.BANK_ACCOUNT_NOT_FOUND, "Cuenta bancaria no encontrada", context={"bank_account_id": str(bank_account_id)})
    bank_account.is_active = not bank_account.is_active
    db.commit()
    db.refresh(bank_account)
    return bank_account
