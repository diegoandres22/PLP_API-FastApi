# src/core/timezone.py
"""Hora local del negocio (Caracas), en un solo lugar."""
from datetime import datetime
from zoneinfo import ZoneInfo

CARACAS_TZ = ZoneInfo("America/Caracas")


def now_caracas() -> datetime:
    """Hora actual de Caracas como datetime naive.

    Reemplaza el `datetime.utcnow() - timedelta(hours=4)` que estaba copiado
    en tres sitios: restar horas a mano deja de ser correcto en cuanto cambie
    el huso o alguien despliegue en otra región. Se devuelve naive porque las
    columnas son DateTime sin zona y el frontend ya asume hora local.
    """
    return datetime.now(CARACAS_TZ).replace(tzinfo=None)
