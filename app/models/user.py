"""
Modelo User: representa a alguien de RR.HH./seguridad que USA la
herramienta. Con multi-tenancy: cada User pertenece a UNA Organization.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.models.database import Base


class UserRole(str, enum.Enum):
    OWNER = "owner"    # único DENTRO de su organización
    ADMIN = "admin"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    email = Column(String, nullable=False, unique=True, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)

    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization")

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"