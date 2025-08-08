from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class BankAccountCreate(BaseModel):
    pay_method: str
    holder_name_cta: str
    document_name: float
    number_cta_1: float
    number_cta_2: Optional[str] = None
    email_cta: Optional[EmailStr] = None

    model_config = {
        "from_attributes": True
    }

class BankAccountResponse(BaseModel):
    id: UUID
    pay_method: str
    holder_name_cta: str
    document_name: float
    number_cta_1: float
    number_cta_2: Optional[str] = None
    email_cta: Optional[EmailStr] = None
    is_active: bool

    model_config = {
        "from_attributes": True
    }

class ToggleActiveResponse(BaseModel):
    id: UUID
    message: str
