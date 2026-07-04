"""
Modelo Person: representa a un empleado o contratista.

Es uno de los dos tipos de "nodo" del grafo de identidad.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship

from app.models.database import Base


class PersonType(str, enum.Enum):
    EMPLOYEE = "employee"
    CONTRACTOR = "contractor"


class PersonStatus(str, enum.Enum):
    ACTIVE = "active"
    OFFBOARDING = "offboarding"   # proceso en curso
    OFFBOARDED = "offboarded"     # proceso completado


class Person(Base):
    __tablename__ = "persons"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    person_type = Column(Enum(PersonType), nullable=False, default=PersonType.EMPLOYEE)
    status = Column(Enum(PersonStatus), nullable=False, default=PersonStatus.ACTIVE)
    department = Column(String, nullable=True)

    hired_at = Column(DateTime, default=datetime.utcnow)
    offboarded_at = Column(DateTime, nullable=True)

    # Relación uno-a-muchos: una persona puede tener muchos accesos (AccessGrant)
    # back_populates conecta esto con el atributo "person" que definiremos en AccessGrant
    access_grants = relationship(
        "AccessGrant", back_populates="person", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Person {self.full_name} ({self.status.value})>"