#!/usr/bin/env python3
"""
Comprueba que la API puede hablar con la base de datos configurada.

Ejecutar desde la raíz de PLP_API-FastApi, con el .env ya configurado:

    python scripts/verificar_conexion.py

Sirve para cualquier proveedor (Neon, Supabase, Render, RDS, local): solo
lee DATABASE_URL. No modifica nada, solo lee.
"""
import os
import sys
import time
from urllib.parse import urlparse

# Permite ejecutarlo desde la raíz del proyecto sin instalar el paquete.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv  # noqa: E402
from sqlalchemy import create_engine, inspect, text  # noqa: E402

load_dotenv()

TABLAS_ESPERADAS = {"raffles", "purchases", "bank_accounts"}

VERDE, ROJO, AMARILLO, GRIS, FIN = "\033[92m", "\033[91m", "\033[93m", "\033[90m", "\033[0m"
OK, ERROR, AVISO = f"{VERDE}OK{FIN}", f"{ROJO}ERROR{FIN}", f"{AMARILLO}AVISO{FIN}"


def main() -> int:
    print("\nVerificación de conexión a la base de datos\n" + "=" * 44)

    # 1. Variables de entorno -------------------------------------------
    url = os.getenv("DATABASE_URL")
    if not url:
        print(f"[{ERROR}] Falta DATABASE_URL. Copia .env.example a .env y complétala.")
        return 1

    partes = urlparse(url)
    host = partes.hostname or "?"
    base = (partes.path or "/").lstrip("/") or "?"
    # Nunca imprimir la contraseña.
    print(f"[{OK}] DATABASE_URL leída  {GRIS}(host: {host} · base: {base}){FIN}")

    sslmode = os.getenv("DB_SSLMODE", "require")
    connect_args = {} if sslmode in ("", "disable") else {"sslmode": sslmode}
    print(f"[{OK}] DB_SSLMODE = {sslmode}")

    if host not in ("localhost", "127.0.0.1") and sslmode in ("", "disable"):
        print(f"[{AVISO}] Conexión remota SIN SSL. En producción usa DB_SSLMODE=require.")

    # 2. Conectividad ----------------------------------------------------
    try:
        engine = create_engine(url, pool_pre_ping=True, connect_args=connect_args)
        inicio = time.perf_counter()
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar_one()
            latencia_ms = (time.perf_counter() - inicio) * 1000
    except Exception as exc:  # noqa: BLE001
        print(f"[{ERROR}] No se pudo conectar.\n       {type(exc).__name__}: {exc}")
        print(
            f"\n{AMARILLO}Causas habituales:{FIN}\n"
            "  · El proyecto está pausado (Supabase pausa el plan gratuito a los 7 días).\n"
            "  · La contraseña del DATABASE_URL tiene caracteres sin codificar (@, :, /, #).\n"
            "  · Tu IP no está permitida en el firewall del proveedor.\n"
            "  · Falta DB_SSLMODE=require en un proveedor que lo exige."
        )
        return 1

    print(f"[{OK}] Conexión establecida  {GRIS}({latencia_ms:.0f} ms){FIN}")
    print(f"       {GRIS}{version.split(' on ')[0]}{FIN}")

    # 3. Esquema ---------------------------------------------------------
    inspector = inspect(engine)
    tablas = set(inspector.get_table_names(schema="public"))

    faltantes = TABLAS_ESPERADAS - tablas
    if faltantes:
        print(f"[{ERROR}] Faltan tablas: {', '.join(sorted(faltantes))}")
        print(f"       Ejecuta:  {AMARILLO}alembic upgrade head{FIN}")
        return 1
    print(f"[{OK}] Tablas presentes: {', '.join(sorted(TABLAS_ESPERADAS))}")

    # 4. Revisión de Alembic --------------------------------------------
    if "alembic_version" in tablas:
        with engine.connect() as conn:
            rev = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
        print(f"[{OK}] Revisión de Alembic aplicada: {rev}")
        if rev != "0002":
            print(f"       {AMARILLO}Se esperaba 0002. Ejecuta: alembic upgrade head{FIN}")
    else:
        print(f"[{AVISO}] Sin tabla alembic_version: la base no está bajo control de migraciones.")
        print(f"       Ejecuta:  {AMARILLO}alembic stamp head{FIN}")

    # 5. Tipos críticos --------------------------------------------------
    # Estos tres tipos fueron la causa del bug de boletos revendidos y de la
    # pérdida de precisión en cédula/cuenta. Se comprueban explícitamente.
    esperado = {
        ("raffles", "tickets_sold_list"): "ARRAY",
        ("bank_accounts", "document_name"): "character varying",
        ("bank_accounts", "number_cta_1"): "character varying",
    }
    with engine.connect() as conn:
        filas = conn.execute(text("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND (table_name, column_name) IN (
                  ('raffles','tickets_sold_list'),
                  ('bank_accounts','document_name'),
                  ('bank_accounts','number_cta_1')
              )
        """)).all()

    problemas = False
    for tabla, columna, tipo in filas:
        if esperado.get((tabla, columna)) != tipo:
            print(f"[{ERROR}] {tabla}.{columna} es '{tipo}', se esperaba '{esperado[(tabla, columna)]}'")
            problemas = True
    if not problemas and filas:
        print(f"[{OK}] Tipos críticos correctos (tickets_sold_list=integer[], identificadores=texto)")

    # 6. Conteo de filas -------------------------------------------------
    with engine.connect() as conn:
        print(f"\n{GRIS}Contenido actual:{FIN}")
        for tabla in sorted(TABLAS_ESPERADAS):
            n = conn.execute(text(f"SELECT count(*) FROM public.{tabla}")).scalar_one()
            print(f"  {tabla:<16} {n:>6} filas")

    estado = "con avisos" if problemas else "correcta"
    print(f"\n{VERDE}Conexión {estado}.{FIN}\n")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
