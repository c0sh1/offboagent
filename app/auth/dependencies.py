"""
Dependencia de FastAPI que protege endpoints: exige un token JWT
válido en el header 'Authorization: Bearer <token>', lo verifica, y
devuelve el User correspondiente.
"""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.models import get_db, User, UserRole
from app.auth.security import decode_access_token

_security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado. Vuelve a iniciar sesión.",
        )

    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Para acciones destructivas/de escritura (crear personas, asignar
    accesos, disparar offboardings). Owner y Admin pueden; un
    'viewer' autenticado puede consultar todo, pero no ejecutar
    estas acciones.
    """
    if current_user.role not in (UserRole.OWNER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador para esta acción.",
        )
    return current_user

def require_owner(current_user: User = Depends(get_current_user)) -> User:
    """Para acciones aún más sensibles (ej. renombrar la empresa) - solo el Owner."""
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere ser el Owner de la empresa para esta acción.",
        )
    return current_user