"""
Endpoints de autenticación: registro y login.

Jerarquía de 3 roles:
- Owner: ÚNICO en todo el sistema. Se crea automáticamente al primer
  usuario que se registra (el bootstrap). Puede crear Admins y Viewers.
- Admin: creado solo por el Owner. Puede operar la herramienta y
  puede crear Viewers - pero NO puede crear más Admins ni otro Owner.
- Viewer: creado por el Owner o un Admin. Solo puede consultar.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
import jwt

from sqlalchemy.orm import Session

from app.models import get_db, User, UserRole
from app.api.schemas import UserCreate, UserOut, LoginRequest, TokenOut
from app.auth.security import hash_password, verify_password, create_access_token, decode_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_caller_from_token(request: Request, db: Session) -> User:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Debes iniciar sesión para crear un usuario nuevo.")

    token = auth_header.removeprefix("Bearer ").strip()
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    caller = db.query(User).filter(User.id == payload.get("sub")).first()
    if caller is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return caller


def _determine_new_user_role(caller: User | None, requested_role: UserRole, is_bootstrap: bool) -> UserRole:
    if is_bootstrap:
        return UserRole.OWNER

    if requested_role == UserRole.OWNER:
        raise HTTPException(status_code=403, detail="Solo puede haber un Owner en el sistema.")

    if caller.role == UserRole.OWNER:
        return requested_role

    if caller.role == UserRole.ADMIN:
        if requested_role != UserRole.VIEWER:
            raise HTTPException(
                status_code=403, detail="Un Admin solo puede crear usuarios de solo lectura (Viewer)."
            )
        return UserRole.VIEWER

    raise HTTPException(status_code=403, detail="No tienes permiso para crear usuarios nuevos.")


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, request: Request, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")

    is_bootstrap = db.query(User).count() == 0
    caller = None if is_bootstrap else _get_caller_from_token(request, db)

    role = _determine_new_user_role(caller, payload.role, is_bootstrap)

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = create_access_token(user.id, user.email)
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user