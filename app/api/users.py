"""
Endpoints de gestión de usuarios del sistema, filtrados a la
organización de quien llama.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db, User, UserRole, UserAuditLog
from app.api.schemas import UserOut, UserAuditLogOut
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/users", tags=["users"])


def _to_user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        organization_name=user.organization.name if user.organization else None,
    )


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    users = db.query(User).filter(User.organization_id == current_user.organization_id).all()
    return [_to_user_out(u) for u in users]


@router.get("/audit-log", response_model=list[UserAuditLogOut])
def get_user_audit_log(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return (
        db.query(UserAuditLog)
        .filter(UserAuditLog.organization_id == current_user.organization_id)
        .order_by(UserAuditLog.timestamp.desc())
        .all()
    )


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    target = (
        db.query(User)
        .filter(User.id == user_id, User.organization_id == current_user.organization_id)
        .first()
    )
    if target is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")

    if target.role == UserRole.OWNER:
        raise HTTPException(status_code=403, detail="No se puede eliminar al Owner de la empresa")

    if current_user.role == UserRole.ADMIN and target.role != UserRole.VIEWER:
        raise HTTPException(
            status_code=403, detail="Un Admin solo puede eliminar usuarios de solo lectura (Viewer)"
        )

    db.add(
        UserAuditLog(
            organization_id=current_user.organization_id,
            actor_email=current_user.email,
            action="delete_user",
            target_email=target.email,
            target_role=target.role.value,
        )
    )
    db.delete(target)
    db.commit()