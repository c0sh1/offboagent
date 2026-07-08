"""
Endpoints de la propia empresa (organización): consultar y renombrar.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import get_db, User, Organization
from app.api.schemas import OrganizationOut, OrganizationUpdate
from app.auth.dependencies import get_current_user, require_owner

router = APIRouter(prefix="/organization", tags=["organization"])


@router.get("", response_model=OrganizationOut)
def get_organization(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    return org


@router.put("", response_model=OrganizationOut)
def update_organization(
    payload: OrganizationUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_owner)
):
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    org.name = payload.name
    db.commit()
    db.refresh(org)
    return org