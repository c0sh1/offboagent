"""
Esquemas Pydantic: definen la "forma" de los datos que entran y
salen por la API. Son distintos de los modelos SQLAlchemy (app/models):
los modelos son la representación en base de datos, estos esquemas
son el contrato público de la API (lo que ve el cliente HTTP).

Separarlos es importante: nos permite, por ejemplo, no exponer
campos internos, o dar forma distinta a la respuesta sin tocar la BD.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import PersonType, PersonStatus, AccessStatus, RiskLevel, OffboardingStatus


class AccessGrantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str | None
    risk_level: RiskLevel
    status: AccessStatus
    system_name: str | None = None  # se rellena a mano en el router (viene de grant.system.name)
    system_id: str | None = None


class PersonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    email: str
    person_type: PersonType
    status: PersonStatus
    department: str | None


class PersonDetailOut(PersonOut):
    access_grants: list[AccessGrantOut]


class OffboardingRequest(BaseModel):
    person_id: str
    initiated_by: str
    reason: str | None = None


class AuditLogEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    system_name: str
    action: str
    result: str
    detail: str | None
    timestamp: datetime


class OrphanFindingOut(BaseModel):
    system_name: str
    external_account_id: str
    email: str
    reason: str
    matched_person_id: str | None
    matched_grant_id: str | None


class PersonCreate(BaseModel):
    full_name: str
    email: str
    person_type: PersonType = PersonType.EMPLOYEE
    department: str | None = None


class SystemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    connector_key: str


class AccessGrantCreate(BaseModel):
    system_id: str
    role: str | None = None
    risk_level: RiskLevel = RiskLevel.LOW


class DashboardStatsOut(BaseModel):
    total_persons: int
    active_persons: int
    offboarding_in_progress: int
    offboarded_persons: int
    systems_count: int
    critical_active_grants: int
    orphaned_access_count: int


class OffboardingEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    person_id: str
    person_full_name: str | None = None
    status: OffboardingStatus
    started_at: datetime
    completed_at: datetime | None
    summary_report: str | None
    log_entries: list[AuditLogEntryOut]