"""
Endpoints de sistemas conectados (Slack, GitHub, AWS IAM, etc.).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import get_db, System
from app.api.schemas import SystemOut

router = APIRouter(prefix="/systems", tags=["systems"])


@router.get("", response_model=list[SystemOut])
def list_systems(db: Session = Depends(get_db)):
    """Lista todos los sistemas conectados, para elegir al asignar un acceso."""
    return db.query(System).all()