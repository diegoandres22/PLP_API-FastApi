# src/core/errors.py
"""
Esquema unificado de errores de la API.

Toda excepción de negocio debe lanzarse con `ApiError`, nunca con
`HTTPException(detail="string suelto")`. Así el cliente (PLP-Admin,
patealaperola) siempre recibe la misma forma en `detail`, sin importar
qué endpoint falló:

    {
      "detail": {
        "code": "RAFFLE_NOT_FOUND",
        "message": "Rifa no encontrada",
        "context": {"raffle_id": "..."}   # o null
      }
    }

`code` es para que el frontend pueda tomar decisiones por tipo de error sin
parsear el texto de `message` (que es para mostrarle al humano). `context`
lleva datos estructurados opcionales (qué campo falló, cuántos boletos
quedan, etc.) — nunca información sensible ni trazas internas.

Los errores que NO pasan por aquí (404 de ruta inexistente, 405 método no
permitido, validación de Pydantic vía FastAPI) se normalizan a esta misma
forma en los exception handlers de `main.py`, así que el frontend nunca ve
un formato distinto sin importar el origen del error.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import HTTPException


class ErrorCode:
    """Catálogo de códigos de error. SCREAMING_SNAKE_CASE, estable: una vez
    publicado un code no se renombra (el frontend puede depender de él)."""

    # Autenticación / autorización (src/core/security.py)
    UNAUTHENTICATED = "UNAUTHENTICATED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    FORBIDDEN = "FORBIDDEN"
    SERVER_MISCONFIGURED = "SERVER_MISCONFIGURED"

    # Rifas
    RAFFLE_NOT_FOUND = "RAFFLE_NOT_FOUND"
    RAFFLE_NOT_ACTIVE = "RAFFLE_NOT_ACTIVE"

    # Compras
    PURCHASE_NOT_FOUND = "PURCHASE_NOT_FOUND"
    PURCHASE_ALREADY_CONFIRMED = "PURCHASE_ALREADY_CONFIRMED"
    PURCHASE_ALREADY_DECLINED = "PURCHASE_ALREADY_DECLINED"
    INVALID_TICKET_COUNT = "INVALID_TICKET_COUNT"
    MIN_PURCHASE_NOT_MET = "MIN_PURCHASE_NOT_MET"
    INSUFFICIENT_TICKETS = "INSUFFICIENT_TICKETS"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"

    # Cuentas bancarias
    BANK_ACCOUNT_NOT_FOUND = "BANK_ACCOUNT_NOT_FOUND"

    # Genéricos (usados por los handlers globales de main.py)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ApiError(HTTPException):
    """HTTPException cuyo `detail` siempre tiene la forma
    {"code", "message", "context"}. Úsala en vez de HTTPException a secas
    para cualquier error de negocio."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        context: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message, "context": context},
            headers=headers,
        )


def error_envelope(code: str, message: str, context: Optional[dict[str, Any]] = None) -> dict:
    """Construye el mismo `detail` que ApiError, para usarlo directamente en
    un JSONResponse (exception handlers globales que no lanzan ApiError)."""
    return {"code": code, "message": message, "context": context}


def error_response(code: str, message: str, context_example: Optional[dict[str, Any]] = None) -> dict:
    """Entrada lista para el parámetro `responses={...}` de un endpoint, para
    que ese error aparezca documentado (con ejemplo real) en /docs en vez de
    quedar implícito. Uso:

        @router.get("/{raffle_id}", responses={404: error_response(
            ErrorCode.RAFFLE_NOT_FOUND, "Rifa no encontrada")})
    """
    return {
        "description": message,
        "content": {
            "application/json": {
                "example": {"detail": error_envelope(code, message, context_example)}
            }
        },
    }
