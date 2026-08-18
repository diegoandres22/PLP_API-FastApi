"""Configuración común de las pruebas.

Crea el esquema una sola vez por sesión de pytest, para que el orden en que
corran los módulos no importe.

Requiere una BD de PRUEBAS en DATABASE_URL (nunca la de producción).
"""
import os

import pytest
from sqlalchemy import create_engine

from src.db.base import Base
# Importar los modelos registra las tablas en el metadata del Base único.
from src.models import bank_account_model, purchasesModel, raffleModel  # noqa: F401


@pytest.fixture(scope="session", autouse=True)
def _esquema():
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL no definida: se omiten las pruebas de integración")
    engine = create_engine(url, connect_args={})
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()
