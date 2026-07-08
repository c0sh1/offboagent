"""
Detección de accesos huérfanos, filtrada por organización.
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Person, PersonStatus, System, AccessGrant, AccessStatus
from app.connectors.registry import get_connector_for_system
from app.config import settings

_KNOWN_SERVICE_ACCOUNT_EMAILS = {
    e.strip() for e in settings.service_account_emails.split(",") if e.strip()
}


@dataclass
class OrphanFinding:
    system_name: str
    external_account_id: str
    email: str
    reason: str
    matched_person_id: str | None = None
    matched_grant_id: str | None = None


def detect_orphaned_access(db: Session, organization_id: str) -> list[OrphanFinding]:
    findings: list[OrphanFinding] = []

    systems = db.query(System).filter(System.organization_id == organization_id).all()
    for system in systems:
        connector = get_connector_for_system(system)
        active_accounts = connector.list_active_accounts()

        for account in active_accounts:
            finding = _evaluate_account(db, system, account, organization_id)
            if finding is not None:
                findings.append(finding)

    return findings


def _evaluate_account(
    db: Session, system: System, account: dict, organization_id: str
) -> OrphanFinding | None:
    email = account.get("email")
    external_id = account.get("external_account_id")

    person = (
        db.query(Person)
        .filter(Person.email == email, Person.organization_id == organization_id)
        .first()
    )

    if person is None:
        if email in _KNOWN_SERVICE_ACCOUNT_EMAILS:
            return None
        return OrphanFinding(
            system_name=system.name, external_account_id=external_id, email=email, reason="unknown_identity"
        )

    grant = _find_grant(db, person.id, system.id)

    if person.status == PersonStatus.OFFBOARDED:
        if grant is not None and grant.status != AccessStatus.ORPHANED:
            grant.status = AccessStatus.ORPHANED
            db.commit()
        return OrphanFinding(
            system_name=system.name,
            external_account_id=external_id,
            email=email,
            reason="person_offboarded",
            matched_person_id=person.id,
            matched_grant_id=grant.id if grant else None,
        )

    if grant is None or grant.status != AccessStatus.ACTIVE:
        return OrphanFinding(
            system_name=system.name,
            external_account_id=external_id,
            email=email,
            reason="no_active_grant_recorded",
            matched_person_id=person.id,
            matched_grant_id=grant.id if grant else None,
        )

    return None


def _find_grant(db: Session, person_id: str, system_id: str) -> AccessGrant | None:
    return (
        db.query(AccessGrant)
        .filter(AccessGrant.person_id == person_id, AccessGrant.system_id == system_id)
        .first()
    )