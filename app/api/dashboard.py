"""
Endpoint de estadísticas agregadas, para la pantalla de dashboard.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import get_db, Person, PersonStatus, System, AccessGrant, AccessStatus, RiskLevel
from app.api.schemas import DashboardStatsOut
from app.services.orphan_detection_service import detect_orphaned_access

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsOut)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_persons = db.query(Person).count()
    active_persons = db.query(Person).filter(Person.status == PersonStatus.ACTIVE).count()
    offboarding_in_progress = db.query(Person).filter(
        Person.status == PersonStatus.OFFBOARDING
    ).count()
    offboarded_persons = db.query(Person).filter(Person.status == PersonStatus.OFFBOARDED).count()
    systems_count = db.query(System).count()
    critical_active_grants = (
        db.query(AccessGrant)
        .filter(AccessGrant.status == AccessStatus.ACTIVE, AccessGrant.risk_level == RiskLevel.CRITICAL)
        .count()
    )
    orphaned_access_count = len(detect_orphaned_access(db))

    return DashboardStatsOut(
        total_persons=total_persons,
        active_persons=active_persons,
        offboarding_in_progress=offboarding_in_progress,
        offboarded_persons=offboarded_persons,
        systems_count=systems_count,
        critical_active_grants=critical_active_grants,
        orphaned_access_count=orphaned_access_count,
    )