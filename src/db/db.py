# src/db/db.py
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "Falta la variable de entorno DATABASE_URL. Copia .env.example a .env "
        "y complétala (ver README)."
    )

# El SSL era obligatorio a fuerza (connect_args sslmode=require), lo que hacía
# imposible levantar la API contra un Postgres local o en Docker. Ahora se
# controla por entorno y sigue siendo 'require' por defecto para producción.
DB_SSLMODE = os.getenv("DB_SSLMODE", "require")
connect_args = {} if DB_SSLMODE in ("", "disable") else {"sslmode": DB_SSLMODE}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
