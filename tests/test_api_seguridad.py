"""Verifica que los endpoints de administración exigen el JWT y que los
públicos siguen abiertos para el comprador anónimo."""
import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)
SECRET = os.getenv("API_JWT_SECRET")


def _token(role="admin", email="admin@plp.com", expirado=False):
    exp = datetime.now(timezone.utc) + (timedelta(minutes=-5) if expirado else timedelta(minutes=5))
    return jwt.encode({"sub": email, "name": "Admin", "role": role, "exp": exp}, SECRET, algorithm="HS256")


def _auth(**kw):
    return {"Authorization": f"Bearer {_token(**kw)}"}


RUTAS_ADMIN = [
    ("get", "/purchase/all/"),
    ("get", "/purchase/confirm_Purchases"),
    ("get", f"/purchase/{uuid.uuid4()}"),
    ("put", f"/purchase/confirm/{uuid.uuid4()}"),
    ("put", f"/purchase/decline/{uuid.uuid4()}"),
    ("delete", f"/raffle/{uuid.uuid4()}"),
    ("post", "/bank-accounts/"),
    ("patch", f"/bank-accounts/{uuid.uuid4()}/toggle"),
]


@pytest.mark.parametrize("metodo,ruta", RUTAS_ADMIN)
def test_endpoints_admin_rechazan_sin_token(metodo, ruta):
    assert getattr(client, metodo)(ruta).status_code == 401


@pytest.mark.parametrize("metodo,ruta", RUTAS_ADMIN)
def test_endpoints_admin_rechazan_token_de_no_admin(metodo, ruta):
    r = getattr(client, metodo)(ruta, headers=_auth(role="usuario"))
    assert r.status_code == 403


def test_token_expirado_es_rechazado():
    r = client.get("/purchase/all/", headers=_auth(expirado=True))
    assert r.status_code == 401
    assert "expirada" in r.json()["detail"].lower()


def test_token_firmado_con_otro_secreto_es_rechazado():
    malo = jwt.encode(
        {"sub": "x@y.com", "role": "admin",
         "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "secreto-incorrecto", algorithm="HS256",
    )
    r = client.get("/purchase/all/", headers={"Authorization": f"Bearer {malo}"})
    assert r.status_code == 401


def test_endpoints_publicos_siguen_abiertos():
    assert client.get("/").status_code == 200
    assert client.get("/raffle/all/").status_code == 200
    assert client.get("/bank-accounts/").status_code == 200


def test_admin_con_token_valido_pasa_la_autorizacion():
    r = client.get("/purchase/all/", headers=_auth())
    assert r.status_code == 200


def test_cabeceras_de_seguridad_presentes():
    h = client.get("/").headers
    assert h["X-Content-Type-Options"] == "nosniff"
    assert h["X-Frame-Options"] == "DENY"
    assert "Referrer-Policy" in h


def test_respuesta_publica_por_numero_de_boleto_no_expone_pii():
    """El endpoint público no debe filtrar datos del comprador."""
    from src.schemas.purchase_schema import PublicPurchaseResponse

    campos = set(PublicPurchaseResponse.model_fields)
    pii = {"buyer_email", "full_name", "phone_number", "payment_reference", "image_url", "holder_cta_bank"}
    assert not (campos & pii), f"El schema público expone PII: {campos & pii}"
