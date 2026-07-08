"""
Modelo Person: representa a un empleado o contratista.
Con multi-tenancy: cada Person pertenece a UNA Organization.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.database import Base


class PersonType(str, enum.Enum):
    EMPLOYEE = "employee"
    CONTRACTOR = "contractor"


class PersonStatus(str, enum.Enum):
    ACTIVE = "active"
    OFFBOARDING = "offboarding"
    OFFBOARDED = "offboarded"


class Person(Base):
    __tablename__ = "persons"
    __table_args__ = (UniqueConstraint("organization_id", "email", name="uq_person_org_email"),)

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    person_type = Column(Enum(PersonType), nullable=False, default=PersonType.EMPLOYEE)
    status = Column(Enum(PersonStatus), nullable=False, default=PersonStatus.ACTIVE)
    department = Column(String, nullable=True)

    hired_at = Column(DateTime, default=datetime.utcnow)
    offboarded_at = Column(DateTime, nullable=True)

    access_grants = relationship(
        "AccessGrant", back_populates="person", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Person {self.full_name} ({self.status.value})>"