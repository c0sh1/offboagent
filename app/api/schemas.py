"""
Esquemas Pydantic: definen la "forma" de los datos que entran y
salen por la API.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import PersonType, PersonStatus, AccessStatus, RiskLevel, OffboardingStatus, UserRole


class AccessGrantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str | None
    risk_level: RiskLevel
    status: AccessStatus
    system_name: str | None = None
    system_id: str | None = None
    external_account_id: str | None = None


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
    has_real_credentials: bool = False


class SystemCreate(BaseModel):
    connector_key: str
    name: str | None = None
    credentials: dict[str, str] | None = None


class ConnectorCredentialFieldOut(BaseModel):
    key: str
    label: str
    secret: bool


class ConnectorTypeOut(BaseModel):
    connector_key: str
    label: str
    category: str
    credential_fields: list[ConnectorCredentialFieldOut]
    has_real_integration: bool


class AccessGrantCreate(BaseModel):
    system_id: str
    role: str | None = None
    risk_level: RiskLevel = RiskLevel.LOW
    external_account_id: str | None = None


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


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, description="Mínimo 8 caracteres")


class UserAuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_email: str
    action: str
    target_email: str
    target_role: str | None
    timestamp: datetime


class PersonAuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_email: str
    action: str
    person_email: str
    detail: str | None
    timestamp: datetime


class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str = Field(min_length=8, description="Mínimo 8 caracteres")
    role: UserRole = UserRole.VIEWER


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: UserRole
    organization_name: str | None = None


class OrganizationRegisterRequest(BaseModel):
    organization_name: str
    full_name: str
    email: str
    password: str = Field(min_length=8, description="Mínimo 8 caracteres")


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str

class OrganizationUpdate(BaseModel):
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"