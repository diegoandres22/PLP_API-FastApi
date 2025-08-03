import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # ID único
    username = Column(String, unique=True, nullable=False)                # Nombre de usuario
    email = Column(String, unique=True, nullable=False)                   # Correo electrónico
    password = Column(String, nullable=False)                             # Contraseña encriptada
    role = Column(String, default="admin")                                # admin o cliente
    is_active = Column(Boolean, default=True)                             # Estado de la cuenta
    created_at = Column(DateTime, server_default=func.now())              # Fecha de creación
