"""
Endpoints del flujo de offboarding: aquí es donde RR.HH. "aprieta el botón".
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db, OffboardingEvent
from app.api.schemas import OffboardingRequest, OffboardingEventOut
from app.services.offboarding_service import initiate_offboarding, execute_offboarding

router = APIRouter(prefix="/offboarding", tags=["offboarding"])


@router.post("", response_model=OffboardingEventOut)
def start_offboarding(payload: OffboardingRequest, db: Session = Depends(get_db)):
    """
    Dispara el offboarding completo de una persona: inicia el evento y
    ejecuta la revocación en todos los sistemas (Fase 4), de forma
    síncrona. En producción, execute_offboarding correría en un
    background job para no bloquear la respuesta HTTP.
    """
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

    return event


@router.get("/{event_id}", response_model=OffboardingEventOut)
def get_offboarding_event(event_id: str, db: Session = Depends(get_db)):
    """Consulta el estado y el log de auditoría de un offboarding concreto."""
    event = db.query(OffboardingEvent).filter(OffboardingEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Evento de offboarding no encontrado")
    return event