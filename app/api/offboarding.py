"""
Endpoints del flujo de offboarding: aquí es donde RR.HH. "aprieta el botón".
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db, OffboardingEvent
from app.api.schemas import OffboardingRequest, OffboardingEventOut, AuditLogEntryOut
from app.services.offboarding_service import initiate_offboarding, execute_offboarding

router = APIRouter(prefix="/offboarding", tags=["offboarding"])


def _serialize_event(event: OffboardingEvent) -> OffboardingEventOut:
    return OffboardingEventOut(
        id=event.id,
        person_id=event.person_id,
        person_full_name=event.person.full_name if event.person else None,
        status=event.status,
        started_at=event.started_at,
        completed_at=event.completed_at,
        summary_report=event.summary_report,
        log_entries=[AuditLogEntryOut.model_validate(log) for log in event.log_entries],
    )


@router.get("", response_model=list[OffboardingEventOut])
def list_offboarding_events(db: Session = Depends(get_db)):
    """Historial completo de offboardings, más recientes primero."""
    events = db.query(OffboardingEvent).order_by(OffboardingEvent.started_at.desc()).all()
    return [_serialize_event(e) for e in events]


@router.post("", response_model=OffboardingEventOut)
def start_offboarding(payload: OffboardingRequest, db: Session = Depends(get_db)):
    try:
        event = initiate_offboarding(
            db,
            person_id=payload.person_id,
            initiated_by=payload.initiated_by,
            reason=payload.reason,
        )
        event = execute_offboarding(db, event.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return _serialize_event(event)


@router.get("/{event_id}", response_model=OffboardingEventOut)
def get_offboarding_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(OffboardingEvent).filter(OffboardingEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Evento de offboarding no encontrado")
    return _serialize_event(event)