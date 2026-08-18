"""Pruebas de la reserva de boletos contra Postgres real.

Cubren las dos formas en que se podían vender boletos duplicados:
  1. El desajuste de tipos text[] vs int[] (fallaba en TODA compra).
  2. La condición de carrera entre compras simultáneas (sin lock de fila).

Requiere DATABASE_URL apuntando a un Postgres de pruebas.
Ejecutar:  pytest tests/ -v
"""
import asyncio
import os
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.base import Base
from src.models.purchasesModel import Purchase
from src.models.raffleModel import Raffle
from src.schemas.purchase_schema import PurchaseCreate
from src.services import purchase_service

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, connect_args={})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

TOTAL_TICKETS = 60


class _FakeUpload:
    """UploadFile mínimo: evita depender de la red en las pruebas."""
    filename = "comprobante.png"
    content_type = "image/png"

    async def read(self):
        return b"contenido-de-prueba"


@pytest.fixture(autouse=True)
def _sin_gcs(monkeypatch):
    # No subir nada a Google Cloud Storage durante las pruebas.
    monkeypatch.setattr(
        purchase_service, "upload_file_to_gcs", lambda *a, **k: "https://ejemplo/comprobante.png"
    )


@pytest.fixture
def rifa():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    raffle = Raffle(
        id=uuid.uuid4(), title="Rifa de prueba", description="d", image="i.png",
        ticket_price=2.0, min_purchase=2, raffle_status=1, state=True,
        trophy="Moto", secondPrize="TV", additionalPrize="Bono",
        total_tickets=TOTAL_TICKETS, tickets_sold_list=[],
    )
    db.add(raffle)
    db.commit()
    rid = raffle.id
    db.close()
    yield rid
    db = SessionLocal()
    db.query(Purchase).filter(Purchase.raffle_id == rid).delete()
    db.query(Raffle).filter(Raffle.id == rid).delete()
    db.commit()
    db.close()


def _comprar(raffle_id, cantidad, email):
    db = SessionLocal()
    try:
        datos = PurchaseCreate(
            buyer_email=email, raffle_id=raffle_id, ticket_count=cantidad,
            payment_method="Pago Movil", payment_reference="REF123",
            full_name="Comprador Prueba", phone_number="+58412000000",
            holder_cta_bank="Comprador Prueba",
        )
        return asyncio.run(purchase_service.create_purchase(db, datos, _FakeUpload()))
    finally:
        db.close()


def test_los_boletos_vendidos_no_se_vuelven_a_ofrecer(rifa):
    """Regresión del bug de tipos: la 2a compra no puede repetir números."""
    primera = _comprar(rifa, 10, "uno@test.com")
    segunda = _comprar(rifa, 10, "dos@test.com")

    solapados = set(primera.ticket_numbers) & set(segunda.ticket_numbers)
    assert not solapados, f"Boletos vendidos dos veces: {sorted(solapados)}"

    db = SessionLocal()
    raffle = db.query(Raffle).filter(Raffle.id == rifa).one()
    assert sorted(raffle.tickets_sold_list) == sorted(
        primera.ticket_numbers + segunda.ticket_numbers
    )
    db.close()


def test_compras_simultaneas_no_asignan_el_mismo_boleto(rifa):
    """6 compras en paralelo de 10 boletos agotan exactamente los 60."""
    with ThreadPoolExecutor(max_workers=6) as pool:
        futuros = [pool.submit(_comprar, rifa, 10, f"c{i}@test.com") for i in range(6)]
        resultados = [f.result() for f in futuros]

    todos = [n for r in resultados for n in r.ticket_numbers]
    assert len(todos) == 60
    assert len(set(todos)) == 60, "Se asignó el mismo boleto a más de un comprador"
    assert set(todos) == set(range(TOTAL_TICKETS))


def test_respeta_total_tickets_y_agota_el_inventario(rifa):
    _comprar(rifa, 50, "casi@test.com")
    with pytest.raises(Exception) as exc:
        _comprar(rifa, 20, "sobrepasa@test.com")
    assert "quedan 10 boletos" in str(exc.value)


def test_rechaza_compra_por_debajo_del_minimo(rifa):
    with pytest.raises(Exception) as exc:
        _comprar(rifa, 1, "poco@test.com")
    assert "al menos 2" in str(exc.value)
