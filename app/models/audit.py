"""
Modelos de auditoría:

- OffboardingEvent: representa "el proceso de offboarding de una persona",
  desde que RR.HH. lo marca hasta que termina.
- AuditLogEntry: cada acción individual ejecutada durante ese proceso
  (una fila por cada AccessGrant revocado, con resultado y timestamp).
  Esto es lo que se exporta como informe para SOC2/ISO27001.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


class OffboardingStatus(str, enum.Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"


class OffboardingEvent(Base):
    __tablename__ = "offboarding_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    person_id = Column(String, ForeignKey("persons.id"), nullable=False, index=True)

    initiated_by = Column(String, nullable=False)   # ej. "hr@empresa.com"
    reason = Column(String, nullable=True)          # ej. "renuncia", "despido", "fin de contrato"
    status = Column(Enum(OffboardingStatus), nullable=False, default=OffboardingStatus.INITIATED)

    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Resumen en lenguaje natural generado por el agente (Fase 5)
    summary_report = Column(Text, nullable=True)

    person = relationship("Person")
    log_entries = relationship(
        "AuditLogEntry", back_populates="offboarding_event", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<OffboardingEvent person={self.person_id} status={self.status.value}>"


    


class AuditLogEntry(Base):
    __tablename__ = "audit_log_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    offboarding_event_id = Column(
        String, ForeignKey("offboarding_events.id"), nullable=False, index=True
    )
    access_grant_id = Column(String, ForeignKey("access_grants.id"), nullable=True)

    action = Column(String, nullable=False)      # ej. "revoke_access"
    system_name = Column(String, nullable=False)  # denormalizado a propósito: el informe debe
                                                    # seguir siendo legible aunque el sistema se borre
    result = Column(String, nullable=False)      # "success" | "failed"
    detail = Column(Text, nullable=True)          # mensaje de error o info adicional

    timestamp = Column(DateTime, default=datetime.utcnow)

    offboarding_event = relationship("OffboardingEvent", back_populates="log_entries")

    def __repr__(self):
        return f"<AuditLogEntry {self.action} -> {self.result}>"