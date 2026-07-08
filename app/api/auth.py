"""
Endpoints de autenticación: registro de empresa nueva, registro de
usuarios adicionales, login, y cambio de contraseña.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db, User, UserRole, UserAuditLog, Organization
from app.api.schemas import (
    UserCreate,
    UserOut,
    LoginRequest,
    TokenOut,
    PasswordChangeRequest,
    OrganizationRegisterRequest,
)
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        organization_name=user.organization.name if user.organization else None,
    )


@router.post("/register-organization", response_model=UserOut, status_code=201)
def register_organization(payload: OrganizationRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")

    organization = Organization(name=payload.organization_name)
    db.add(organization)
    db.flush()

    owner = User(
        organization_id=organization.id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=UserRole.OWNER,
    )
    db.add(owner)

    db.add(
        UserAuditLog(
            organization_id=organization.id,
            actor_email=owner.email,
            action="create_user",
            target_email=owner.email,
            target_role=UserRole.OWNER.value,
        )
    )

    db.commit()
    db.refresh(owner)
    return _to_user_out(owner)


@router.post("/register", response_model=UserOut, status_code=201)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")

    if payload.role == UserRole.OWNER:
        raise HTTPException(status_code=403, detail="Solo puede haber un Owner por empresa.")

    if current_user.role == UserRole.ADMIN and payload.role != UserRole.VIEWER:
        raise HTTPException(
            status_code=403, detail="Un Admin solo puede crear usuarios de solo lectura (Viewer)."
        )
    if current_user.role == UserRole.VIEWER:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear usuarios nuevos.")

    user = User(
        organization_id=current_user.organization_id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)

    db.add(
        UserAuditLog(
            organization_id=current_user.organization_id,
            actor_email=current_user.email,
            action="create_user",
            target_email=user.email,
            target_role=payload.role.value,
        )
    )

    db.commit()
    db.refresh(user)
    return _to_user_out(user)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = create_access_token(user.id, user.email)
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return _to_user_out(current_user)


@router.post("/me/password", status_code=204)
def change_my_password(
    payload: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="La contraseña actual no es correcta")

    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()