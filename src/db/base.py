# src/db/base.py
"""
Base declarativa ÚNICA para todos los modelos.

Antes cada modelo llamaba a su propio declarative_base(), así que existían
tres MetaData separados: Alembic no podía ver el esquema completo y las
relaciones entre tablas eran invisibles para SQLAlchemy. Todos los modelos
deben importar este Base.
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
