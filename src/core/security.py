# src/core/security.py
"""
Verificación del JWT de administrador.

El token NO lo emite esta API: lo firma el servidor de Next.js del panel
admin (ver PLP-Admin/src/app/api/token/route.ts) después de validar la
sesión de NextAuth (Google + allowlist de ALLOWED_EMAILS). Aquí solo se
verifica firma + expiración + rol, con el mismo secreto compartido
(API_JWT_SECRET). El navegador nunca ve ese secreto.
"""
import os
from typing import Optional

import jwt
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.core.errors import ApiError, ErrorCode

API_JWT_SECRET = os.getenv("API_JWT_SECRET")
API_JWT_ALGORITHM = "HS256"

_bearer_scheme = HTTPBearer(auto_error=False)


class AdminClaims(BaseModel):
    email: str
    name: Optional[str] = None
    role: str


def get_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> AdminClaims:
    if credentials is None:
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=ErrorCode.UNAUTHENTICATED,
            message="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not API_JWT_SECRET:
        # Falta configurar el secreto en el entorno: no degradar a "sin auth".
        raise ApiError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=ErrorCode.SERVER_MISCONFIGURED,
            message="Autenticación no configurada en el servidor",
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            API_JWT_SECRET,
            algorithms=[API_JWT_ALGORITHM],
            options={"require": ["exp", "sub", "role"]},
        )
    except jwt.ExpiredSignatureError:
        raise ApiError(status.HTTP_401_UNAUTHORIZED, ErrorCode.SESSION_EXPIRED, "Sesión expirada")
    except jwt.InvalidTokenError:
        raise ApiError(status.HTTP_401_UNAUTHORIZED, ErrorCode.INVALID_TOKEN, "Token inválido")

    if payload.get("role") != "admin":
        raise ApiError(status.HTTP_403_FORBIDDEN, ErrorCode.FORBIDDEN, "No autorizado")

    return AdminClaims(email=payload["sub"], name=payload.get("name"), role=payload["role"])
