"""
Endpoints de sistemas conectados. Cada empresa añade y configura sus
propios sistemas, con sus propias credenciales (cifradas).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db, System, User
from app.api.schemas import SystemOut, SystemCreate, ConnectorTypeOut, ConnectorCredentialFieldOut
from app.auth.dependencies import get_current_user, require_admin
from app.connectors.registry import CONNECTOR_TYPES
from app.services.credentials_crypto import encrypt_credentials

router = APIRouter(prefix="/systems", tags=["systems"])


@router.get("/connector-types", response_model=list[ConnectorTypeOut])
def list_connector_types(current_user: User = Depends(get_current_user)):
    return [
        ConnectorTypeOut(
            connector_key=key,
            label=meta["label"],
            category=meta["category"],
            credential_fields=[ConnectorCredentialFieldOut(**f) for f in meta["credential_fields"]],
            has_real_integration=len(meta["credential_fields"]) > 0,
        )
        for key, meta in CONNECTOR_TYPES.items()
    ]


@router.get("", response_model=list[SystemOut])
def list_systems(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    systems = db.query(System).filter(System.organization_id == current_user.organization_id).all()
    return [
        SystemOut(
            id=s.id,
            name=s.name,
            category=s.category.value,
            connector_key=s.connector_key,
            has_real_credentials=bool(s.encrypted_credentials),
        )
        for s in systems
    ]


@router.post("", response_model=SystemOut, status_code=201)
def create_system(
    payload: SystemCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    meta = CONNECTOR_TYPES.get(payload.connector_key)
    if meta is None:
        raise HTTPException(status_code=400, detail=f"Tipo de conector desconocido: {payload.connector_key}")

    existing = (
        db.query(System)
        .filter(
            System.organization_id == current_user.organization_id,
            System.connector_key == payload.connector_key,
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=400, detail="Tu empresa ya tiene un sistema de este tipo conectado")

    encrypted = None
    if payload.credentials:
        required_keys = {f["key"] for f in meta["credential_fields"]}
        missing = required_keys - set(payload.credentials.keys())
        if missing:
            raise HTTPException(status_code=400, detail=f"Faltan credenciales requeridas: {', '.join(missing)}")
        encrypted = encrypt_credentials(payload.credentials)

    system = System(
        organization_id=current_user.organization_id,
        name=payload.name or meta["label"],
        category=meta["category"],
        connector_key=payload.connector_key,
        encrypted_credentials=encrypted,
    )
    db.add(system)
    db.commit()
    db.refresh(system)

    return SystemOut(
        id=system.id,
        name=system.name,
        category=system.category.value,
        connector_key=system.connector_key,
        has_real_credentials=bool(system.encrypted_credentials),
    )