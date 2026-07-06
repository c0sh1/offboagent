"""
Modelo User: representa a alguien de RR.HH./seguridad que USA la
herramienta (inicia sesión, dispara offboardings, revisa alertas).
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum

from app.models.database import Base


class UserRole(str, enum.Enum):
    OWNER = "owner"    # único en todo el sistema, el bootstrap inicial
    ADMIN = "admin"    # crea personas, asigna accesos, dispara offboardings; puede crear viewers
    VIEWER = "viewer"  # solo puede consultar (dashboard, historial, huérfanos)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, nullable=False, unique=True, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"