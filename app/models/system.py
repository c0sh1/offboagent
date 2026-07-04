"""
Modelo System: representa una herramienta SaaS conectada
(Slack, GitHub, AWS IAM, Google Workspace, Notion, Jira, Zoom...).

Es el segundo tipo de "nodo" del grafo de identidad.
"""
import enum
import uuid

from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship

from app.models.database import Base


class SystemCategory(str, enum.Enum):
    COMMUNICATION = "communication"   # Slack, Zoom
    CODE = "code"                     # GitHub, GitLab
    CLOUD_INFRA = "cloud_infra"       # AWS IAM, GCP
    PRODUCTIVITY = "productivity"     # Google Workspace, Notion, Jira


class System(Base):
    __tablename__ = "systems"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)           # ej. "Slack"
    category = Column(Enum(SystemCategory), nullable=False)
    connector_key = Column(String, nullable=False, unique=True)  # ej. "slack" -> usado para elegir el conector en la Fase 3

    # Relación inversa: un sistema tiene muchas concesiones de acceso
    access_grants = relationship("AccessGrant", back_populates="system")

    def __repr__(self):
        return f"<System {self.name}>"