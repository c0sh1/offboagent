"""
Detección de accesos huérfanos.

Un acceso "huérfano" es aquel que sigue existiendo (activo) en un
sistema externo, pero que según nuestro grafo de identidad NO debería
seguir activo: la persona ya fue offboardeada, o no hay ningún
AccessGrant registrado que lo explique (acceso "en la sombra", dado
fuera de nuestro proceso normal).

Este es exactamente el problema del caso real citado al inicio: un
contratista despedido seguía con acceso a producción 3 meses después,
y nadie lo detectó hasta que inició sesión desde otro país. Esta
función es la que debería correr periódicamente (ej. un cron diario)
para detectar ese escenario ANTES de que se convierta en un incidente,
en vez de depender de un Word que nadie sigue.
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Person, PersonStatus, System, AccessGrant, AccessStatus
from app.connectors.registry import get_connector


@dataclass
class OrphanFinding:
    system_name: str
    external_account_id: str
    email: str
    # "person_offboarded" | "unknown_identity" | "no_active_grant_recorded"
    reason: str
    matched_person_id: str | None = None
    matched_grant_id: str | None = None


def detect_orphaned_access(db: Session) -> list[OrphanFinding]:
    """
    Recorre TODOS los sistemas conectados, pregunta a cada conector
    quién tiene acceso activo AHORA MISMO (list_active_accounts), y lo
    contrasta contra nuestro grafo de identidad.
    """
    findings: list[OrphanFinding] = []

    for system in db.query(System).all():
        connector = get_connector(system.connector_key)
        active_accounts = connector.list_active_accounts()

        for account in active_accounts:
            finding = _evaluate_account(db, system, account)
            if finding is not None:
                findings.append(finding)

    return findings


def _evaluate_account(db: Session, system: System, account: dict) -> OrphanFinding | None:
    email = account.get("email")
    external_id = account.get("external_account_id")

    person = db.query(Person).filter(Person.email == email).first()

    if person is None:
        return OrphanFinding(
            system_name=system.name,
            external_account_id=external_id,
            email=email,
            reason="unknown_identity",
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