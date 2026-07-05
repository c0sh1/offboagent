"""
Endpoints relacionados con personas (empleados/contratistas).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db, Person
from app.api.schemas import PersonOut, PersonDetailOut, AccessGrantOut

router = APIRouter(prefix="/persons", tags=["persons"])


@router.get("", response_model=list[PersonOut])
def list_persons(db: Session = Depends(get_db)):
    """Lista todas las personas registradas."""
    return db.query(Person).all()


@router.get("/{person_id}", response_model=PersonDetailOut)
def get_person(person_id: str, db: Session = Depends(get_db)):
    """Detalle de una persona, incluyendo TODOS sus accesos (el grafo de identidad)."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    # Construimos manualmente los AccessGrantOut para incluir system_name,
    # que vive en una tabla relacionada (grant.system.name), no directamente
    # en AccessGrant.
    grants_out = [
        AccessGrantOut(
            id=g.id,
            role=g.role,
            risk_level=g.risk_level,
            status=g.status,
            system_name=g.system.name,
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