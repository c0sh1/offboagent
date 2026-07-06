"""
Modelo User: representa a alguien de RR.HH./seguridad que USA la
herramienta (inicia sesión, dispara offboardings, revisa alertas).

Importante: esto es distinto de Person. Person es la gente que se
offboardea (empleados/contratistas de la empresa cliente). User es
quien opera el sistema. Un User normalmente nunca es también un
Person en el mismo grafo (aunque nada lo impide técnicamente).
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime

from app.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, nullable=False, unique=True, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)  # NUNCA se guarda en texto plano

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email}>"