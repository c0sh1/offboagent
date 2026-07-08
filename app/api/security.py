"""
Endpoints de seguridad: detección proactiva de accesos huérfanos,
filtrada a la organización de quien llama.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import get_db, User
from app.api.schemas import OrphanFindingOut
from app.services.orphan_detection_service import detect_orphaned_access
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/security", tags=["security"])


@router.get("/orphaned-access", response_model=list[OrphanFindingOut])
def get_orphaned_access(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    findings = detect_orphaned_access(db, current_user.organization_id)
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