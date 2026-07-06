"""
Endpoints de sistemas conectados (Slack, GitHub, AWS IAM, etc.).
Requiere autenticación.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import get_db, System, User
from app.api.schemas import SystemOut
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/systems", tags=["systems"])


@router.get("", response_model=list[SystemOut])
def list_systems(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Lista todos los sistemas conectados, para elegir al asignar un acceso."""
    return db.query(System).all()