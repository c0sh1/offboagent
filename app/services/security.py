"""
Endpoints de seguridad: detección proactiva de accesos huérfanos.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import get_db
from app.api.schemas import OrphanFindingOut
from app.services.orphan_detection_service import detect_orphaned_access

router = APIRouter(prefix="/security", tags=["security"])


@router.get("/orphaned-access", response_model=list[OrphanFindingOut])
def get_orphaned_access(db: Session = Depends(get_db)):
    """
    Compara, sistema por sistema, quién tiene acceso activo AHORA
    MISMO contra quién debería tenerlo según nuestro grafo de
    identidad. Pensado para correr periódicamente (cron diario) en
    producción, no solo a demanda.
    """
    findings = detect_orphaned_access(db)
    return [
        OrphanFindingOut(
            system_name=f.system_name,
            external_account_id=f.external_account_id,
            email=f.email,
            reason=f.reason,
            matched_person_id=f.matched_person_id,
            matched_grant_id=f.matched_grant_id,
        )
        for f in findings
    ]