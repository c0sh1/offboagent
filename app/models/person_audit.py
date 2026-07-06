"""
Modelo PersonAuditLog: registra quién creó una Person y quién le
asignó cada AccessGrant, y cuándo.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime

from app.models.database import Base


class PersonAuditLog(Base):
    __tablename__ = "person_audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    actor_email = Column(String, nullable=False)
    action = Column(String, nullable=False)
    person_email = Column(String, nullable=False)
    detail = Column(String, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PersonAuditLog {self.actor_email} -> {self.action} -> {self.person_email}>"