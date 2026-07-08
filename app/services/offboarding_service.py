"""
OffboardingService: la lógica de negocio central del producto.

Flujo:
1. `initiate_offboarding`: RR.HH. marca a alguien -> se crea un
   OffboardingEvent y la persona pasa a estado OFFBOARDING.
2. `execute_offboarding`: se recorren TODOS sus accesos activos,
   ordenados por nivel de riesgo (los más críticos primero, ej.
   admin de AWS antes que un canal de Slack), y se revoca cada uno
   a través de su conector correspondiente (Fase 3), registrando
   cada acción en el log de auditoría (Fase 2).

Nota: initiate y execute están separados a propósito. En producción,
`initiate` lo dispara RR.HH. (vía API), y `execute` puede correr en
un background job/cola — así una revocación lenta no bloquea la
respuesta HTTP. Para el MVP los llamamos uno tras otro.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    Person,
    PersonStatus,
    AccessGrant,
    AccessStatus,
    RiskLevel,
    OffboardingEvent,
    OffboardingStatus,
    AuditLogEntry,
)
from app.connectors.registry import get_connector_for_system

# Orden de prioridad de revocación: los accesos más críticos se
# revocan primero (ej. admin de AWS antes que un canal de Slack).
_RISK_PRIORITY = {
    RiskLevel.CRITICAL: 0,
    RiskLevel.HIGH: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.LOW: 3,
}


def initiate_offboarding(
    db: Session, person_id: str, initiated_by: str, reason: str | None = None
) -> OffboardingEvent:
    """Crea el evento de offboarding y marca a la persona como 'en proceso'."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        raise ValueError(f"No existe ninguna persona con id={person_id}")

    person.status = PersonStatus.OFFBOARDING

    event = OffboardingEvent(
        organization_id=person.organization_id,
        person_id=person.id,
        initiated_by=initiated_by,
        reason=reason,
        status=OffboardingStatus.INITIATED,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def execute_offboarding(db: Session, offboarding_event_id: str) -> OffboardingEvent:
    """
    Ejecuta la revocación real de todos los accesos activos de la
    persona asociada a este evento, y deja constancia de cada paso.
    """
    event = db.query(OffboardingEvent).filter(OffboardingEvent.id == offboarding_event_id).first()
    if event is None:
        raise ValueError(f"No existe ningún OffboardingEvent con id={offboarding_event_id}")

    event.status = OffboardingStatus.IN_PROGRESS
    db.commit()

    person = event.person
    active_grants = [g for g in person.access_grants if g.status == AccessStatus.ACTIVE]

    # Ordenamos: los accesos más peligrosos se revocan primero
    active_grants.sort(key=lambda g: _RISK_PRIORITY.get(g.risk_level, 99))

    had_errors = False

    for grant in active_grants:
        had_errors |= _revoke_single_grant(db, event, grant)

    person.status = PersonStatus.OFFBOARDED
    person.offboarded_at = datetime.utcnow()

    event.status = (
        OffboardingStatus.COMPLETED_WITH_ERRORS if had_errors else OffboardingStatus.COMPLETED
    )
    event.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(event)
    return event


def revoke_grant_by_id(db: Session, event: OffboardingEvent, grant_id: str) -> dict:
    """
    Revoca un AccessGrant concreto por su id. Pensada para ser llamada
    desde una herramienta del agente (Fase 5), donde el LLM decide QUÉ
    grant_id revocar, pero la ejecución real sigue pasando por el mismo
    código (_revoke_single_grant) que usa el flujo determinista.
    """
    grant = db.query(AccessGrant).filter(AccessGrant.id == grant_id).first()
    if grant is None:
        return {"success": False, "detail": f"No existe ningún AccessGrant con id={grant_id}"}

    had_error = _revoke_single_grant(db, event, grant)
    return {
        "success": not had_error,
        "system": grant.system.name,
        "status": grant.status.value,
    }


def _revoke_single_grant(db: Session, event: OffboardingEvent, grant: AccessGrant) -> bool:
    """
    Revoca un único AccessGrant a través de su conector, y registra
    el resultado en el log de auditoría.

    Devuelve True si HUBO error (para que execute_offboarding sepa
    si debe marcar el evento como 'completado con errores').
    """
    system = grant.system
    connector = get_connector_for_system(system)

    result = connector.revoke_access(grant.external_account_id or "unknown")

    if result.success:
        grant.status = AccessStatus.REVOKED
        grant.revoked_at = datetime.utcnow()
    else:
        grant.status = AccessStatus.REVOCATION_FAILED

    log_entry = AuditLogEntry(
        offboarding_event_id=event.id,
        access_grant_id=grant.id,
        action="revoke_access",
        system_name=system.name,
        result="success" if result.success else "failed",
        detail=result.detail,
    )
    db.add(log_entry)
    db.commit()

    return not result.success