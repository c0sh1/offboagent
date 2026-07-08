"""
Endpoint de estadísticas agregadas, filtradas a la organización de quien llama.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import get_db, Person, PersonStatus, System, AccessGrant, AccessStatus, RiskLevel, User
from app.api.schemas import DashboardStatsOut
from app.services.orphan_detection_service import detect_orphaned_access
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsOut)
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    org_id = current_user.organization_id

    total_persons = db.query(Person).filter(Person.organization_id == org_id).count()
    active_persons = (
        db.query(Person).filter(Person.organization_id == org_id, Person.status == PersonStatus.ACTIVE).count()
    )
    offboarding_in_progress = (
        db.query(Person)
        .filter(Person.organization_id == org_id, Person.status == PersonStatus.OFFBOARDING)
        .count()
    )
    offboarded_persons = (
        db.query(Person)
        .filter(Person.organization_id == org_id, Person.status == PersonStatus.OFFBOARDED)
        .count()
    )
    systems_count = db.query(System).filter(System.organization_id == org_id).count()

    critical_active_grants = (
        db.query(AccessGrant)
        .join(Person, AccessGrant.person_id == Person.id)
        .filter(
            Person.organization_id == org_id,
            AccessGrant.status == AccessStatus.ACTIVE,
            AccessGrant.risk_level == RiskLevel.CRITICAL,
        )
        .count()
    )
    orphaned_access_count = len(detect_orphaned_access(db, org_id))

    return DashboardStatsOut(
        total_persons=total_persons,
        active_persons=active_persons,
        offboarding_in_progress=offboarding_in_progress,
        offboarded_persons=offboarded_persons,
        systems_count=systems_count,
        critical_active_grants=critical_active_grants,
        orphaned_access_count=orphaned_access_count,
    )