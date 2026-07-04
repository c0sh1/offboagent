"""
Modelo AccessGrant: la "arista" del grafo de identidad.

Representa el hecho de que una Person tiene acceso a un System,
con qué rol, desde cuándo, y si ese acceso sigue activo o fue revocado.

Esta es la tabla que consultamos constantemente para responder:
- "¿qué accesos tiene esta persona?"
- "¿quién tiene acceso a este sistema?"
- "¿qué accesos siguen activos tras un offboarding?" (accesos huérfanos)
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.models.database import Base


class AccessStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    REVOCATION_FAILED = "revocation_failed"   # el intento de revocar falló (importante para alertar)
    ORPHANED = "orphaned"                     # detectado como acceso que no debería existir


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AccessGrant(Base):
    __tablename__ = "access_grants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    person_id = Column(String, ForeignKey("persons.id"), nullable=False, index=True)
    system_id = Column(String, ForeignKey("systems.id"), nullable=False, index=True)

    # Identificador de la cuenta en el sistema externo (ej. user_id de Slack)
    external_account_id = Column(String, nullable=True)

    # Rol o nivel de permiso dentro de ese sistema (ej. "admin", "member", "read-only")
    role = Column(String, nullable=True)

    status = Column(Enum(AccessStatus), nullable=False, default=AccessStatus.ACTIVE)
    risk_level = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.LOW)

    granted_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)

    # Relaciones ORM: nos permiten hacer access_grant.person.full_name
    # o access_grant.system.name sin escribir queries manuales
    person = relationship("Person", back_populates="access_grants")
    system = relationship("System", back_populates="access_grants")

    def __repr__(self):
        return f"<AccessGrant person={self.person_id} system={self.system_id} status={self.status.value}>"