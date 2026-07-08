"""
Modelo UserAuditLog: registra quién creó o eliminó a qué usuario del
sistema, y cuándo.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey

from app.models.database import Base


class UserAuditLog(Base):
    __tablename__ = "user_audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    actor_email = Column(String, nullable=False)
    action = Column(String, nullable=False)
    target_email = Column(String, nullable=False)
    target_role = Column(String, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UserAuditLog {self.actor_email} -> {self.action} -> {self.target_email}>"