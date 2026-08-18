from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

# document_name (cédula/RIF) y number_cta_1 (número de cuenta/teléfono) son
# identificadores, no cantidades: como float perdían dígitos y ceros a la
# izquierda. Ahora viajan y se almacenan como texto, con longitud acotada.


class BankAccountCreate(BaseModel):
    pay_method: str = Field(..., min_length=1, max_length=200)
    holder_name_cta: Optional[str] = Field(default=None, max_length=200)
    document_name: Optional[str] = Field(default=None, max_length=50)
    number_cta_1: Optional[str] = Field(default=None, max_length=50)
    number_cta_2: Optional[str] = Field(default=None, max_length=200)
    email_cta: Optional[EmailStr] = None

    model_config = {
        "from_attributes": True
    }


class BankAccountResponse(BaseModel):
    id: UUID
    pay_method: str
    holder_name_cta: Optional[str] = None
    document_name: Optional[str] = None
    number_cta_1: Optional[str] = None
    number_cta_2: Optional[str] = None
    email_cta: Optional[EmailStr] = None
    is_active: bool

    model_config = {
        "from_attributes": True
    }


class ToggleActiveResponse(BaseModel):
    id: UUID
    message: str
