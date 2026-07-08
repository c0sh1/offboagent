"""
Endpoints relacionados con personas (empleados/contratistas).
Todas las consultas están filtradas por la organización de quien llama.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db, Person, System, AccessGrant, User, PersonAuditLog
from app.api.schemas import (
    PersonOut,
    PersonDetailOut,
    PersonCreate,
    AccessGrantOut,
    AccessGrantCreate,
    PersonAuditLogOut,
)
from app.auth.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("", response_model=PersonOut, status_code=201)
def create_person(
    payload: PersonCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    existing = (
        db.query(Person)
        .filter(Person.email == payload.email, Person.organization_id == current_user.organization_id)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=400, detail="Ya existe una persona con ese email en tu empresa")

    person = Person(
        organization_id=current_user.organization_id,
        full_name=payload.full_name,
        email=payload.email,
        person_type=payload.person_type,
        department=payload.department,
    )
    db.add(person)

    db.add(
        PersonAuditLog(
            organization_id=current_user.organization_id,
            actor_email=current_user.email,
            action="create_person",
            person_email=person.email,
            detail=f"Tipo: {payload.person_type.value}"
            + (f", departamento: {payload.department}" if payload.department else ""),
        )
    )

    db.commit()
    db.refresh(person)
    return person


@router.get("", response_model=list[PersonOut])
def list_persons(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Person).filter(Person.organization_id == current_user.organization_id).all()


@router.get("/audit-log", response_model=list[PersonAuditLogOut])
def get_person_audit_log(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(PersonAuditLog)
        .filter(PersonAuditLog.organization_id == current_user.organization_id)
        .order_by(PersonAuditLog.timestamp.desc())
        .all()
    )


@router.get("/{person_id}", response_model=PersonDetailOut)
def get_person(
    person_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    person = (
        db.query(Person)
        .filter(Person.id == person_id, Person.organization_id == current_user.organization_id)
        .first()
    )
    if person is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    grants_out = [
        AccessGrantOut(
            id=g.id,
            role=g.role,
            risk_level=g.risk_level,
            status=g.status,
            system_name=g.system.name,
            system_id=g.system_id,
            external_account_id=g.external_account_id,
        )
        for g in person.access_grants
    ]

    return PersonDetailOut(
        id=person.id,
        full_name=person.full_name,
        email=person.email,
        person_type=person.person_type,
        status=person.status,
        department=person.department,
        access_grants=grants_out,
    )


@router.post("/{person_id}/access-grants", response_model=AccessGrantOut, status_code=201)
def add_access_grant(
    person_id: str,
    payload: AccessGrantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    person = (
        db.query(Person)
        .filter(Person.id == person_id, Person.organization_id == current_user.organization_id)
        .first()
    )
    if person is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    system = (
        db.query(System)
        .filter(System.id == payload.system_id, System.organization_id == current_user.organization_id)
        .first()
    )
    if system is None:
        raise HTTPException(status_code=404, detail="Sistema no encontrado")

    grant = AccessGrant(
        person_id=person.id,
        system_id=system.id,
        role=payload.role,
        risk_level=payload.risk_level,
        external_account_id=payload.external_account_id,
    )
    db.add(grant)

    db.add(
        PersonAuditLog(
            organization_id=current_user.organization_id,
            actor_email=current_user.email,
            action="assign_access_grant",
            person_email=person.email,
            detail=f"Sistema: {system.name}, rol: {payload.role or '—'}, riesgo: {payload.risk_level.value}",
        )
    )

    db.commit()
    db.refresh(grant)

    return AccessGrantOut(
        id=grant.id,
        role=grant.role,
        risk_level=grant.risk_level,
        status=grant.status,
        system_name=system.name,
        system_id=system.id,
        external_account_id=grant.external_account_id,
    )