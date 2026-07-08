"""
Modelo Organization: representa a una empresa cliente del producto.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime

from app.models.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Organization {self.name}>"