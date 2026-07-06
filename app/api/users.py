"""
Endpoints de gestión de usuarios del sistema (no confundir con
Person: estos son quienes OPERAN la herramienta).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db, User, UserRole
from app.api.schemas import UserOut
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Solo un admin/owner puede ver la lista de usuarios del sistema."""
    return db.query(User).all()


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    """
    Elimina un usuario. Reglas, en el mismo espíritu que la creación:
    - Nadie puede eliminarse a sí mismo (evita quedarte fuera por error).
    - Nadie puede eliminar al Owner (es único, el sistema lo necesita).
    - Un Admin solo puede eliminar Viewers (no a otros Admins).
    - El Owner puede eliminar tanto Admins como Viewers.
    """
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

    db.delete(target)
    db.commit()