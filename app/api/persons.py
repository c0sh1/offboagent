"""
Endpoints relacionados con personas (empleados/contratistas).

Todos los endpoints requieren autenticación (current_user), excepto
ninguno aquí - este router entero está protegido.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db, Person, System, AccessGrant, User
from app.api.schemas import PersonOut, PersonDetailOut, PersonCreate, AccessGrantOut, AccessGrantCreate
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("", response_model=PersonOut, status_code=201)
def create_person(
    payload: PersonCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Registra una nueva persona (empleado/contratista) en el grafo de identidad."""
    existing = db.query(Person).filter(Person.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Ya existe una persona con ese email")

    person = Person(
        full_name=payload.full_name,
        email=payload.email,
        person_type=payload.person_type,
        department=payload.department,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@router.get("", response_model=list[PersonOut])
def list_persons(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Lista todas las personas registradas."""
    return db.query(Person).all()


@router.get("/{person_id}", response_model=PersonDetailOut)
def get_person(
    person_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Detalle de una persona, incluyendo TODOS sus accesos (el grafo de identidad)."""
    person = db.query(Person).filter(Person.id == person_id).first()
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
    current_user: User = Depends(get_current_user),
):
    """
    Asigna un acceso nuevo a una persona en un sistema concreto.
    Esta es la pieza que completa el ciclo de vida: crear persona ->
    asignarle accesos -> (más adelante) offboardearla con sentido.
    """
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    system = db.query(System).filter(System.id == payload.system_id).first()
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