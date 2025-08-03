from sqlalchemy import Column, String, Boolean

class BankAccount(Base):
    __tablename__ = 'bank_accounts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # ID único
    bank_name = Column(String, nullable=False)                             # Nombre del banco
    account_number = Column(String, nullable=False)                        # Nº de cuenta
    account_holder = Column(String, nullable=False)                        # Titular de la cuenta
    account_type = Column(String, nullable=True)                           # Ahorro/Corriente
    currency = Column(String, nullable=True)                               # VES/USD
    zelle_email = Column(String, nullable=True)                            # Email de Zelle
    is_active = Column(Boolean, default=True)                              # Activa para transferencias
