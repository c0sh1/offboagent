"""
Modelo System: representa una herramienta SaaS conectada.
Con multi-tenancy: cada System pertenece a UNA Organization y guarda
sus propias credenciales cifradas.
"""
import enum
import uuid

from sqlalchemy import Column, String, Enum, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


class SystemCategory(str, enum.Enum):
    COMMUNICATION = "communication"
    CODE = "code"
    CLOUD_INFRA = "cloud_infra"
    PRODUCTIVITY = "productivity"


class System(Base):
    __tablename__ = "systems"
    __table_args__ = (
        UniqueConstraint("organization_id", "connector_key", name="uq_system_org_connector"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    name = Column(String, nullable=False)
    category = Column(Enum(SystemCategory), nullable=False)
    connector_key = Column(String, nullable=False)

    encrypted_credentials = Column(Text, nullable=True)

    access_grants = relationship("AccessGrant", back_populates="system")

    def __repr__(self):
        return f"<System {self.name}>"