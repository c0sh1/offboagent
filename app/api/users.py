"""
Endpoints de gestión de usuarios del sistema.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db, User, UserRole, UserAuditLog
from app.api.schemas import UserOut, UserAuditLogOut
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(User).all()


@router.get("/audit-log", response_model=list[UserAuditLogOut])
def get_user_audit_log(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(UserAuditLog).order_by(UserAuditLog.timestamp.desc()).all()


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    target = db.query(User).filter(User.id == user_id).first()
    if target is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")

    if target.role == UserRole.OWNER:
        raise HTTPException(status_code=403, detail="No se puede eliminar al Owner del sistema")

    if current_user.role == UserRole.ADMIN and target.role != UserRole.VIEWER:
        raise HTTPException(
            status_code=403, detail="Un Admin solo puede eliminar usuarios de solo lectura (Viewer)"
        )

    db.add(
        UserAuditLog(
            actor_email=current_user.email,
            action="delete_user",
            target_email=target.email,
            target_role=target.role.value,
        )
    )
    db.delete(target)
    db.commit()