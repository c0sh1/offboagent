"""
Punto único de importación de todos los modelos.

Importar todo aquí es importante por dos razones:
1. Comodidad: en el resto del proyecto podemos hacer
   `from app.models import Person, System, AccessGrant`
2. Necesario para SQLAlchemy: cuando llamemos a Base.metadata.create_all(),
   necesita que Python haya "visto" (importado) todas las clases de modelo
   para saber qué tablas crear.
"""
from app.models.database import Base, engine, SessionLocal, get_db
from app.models.person import Person, PersonType, PersonStatus
from app.models.system import System, SystemCategory
from app.models.access_grant import AccessGrant, AccessStatus, RiskLevel
from app.models.audit import OffboardingEvent, OffboardingStatus, AuditLogEntry

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "Person",
    "PersonType",
    "PersonStatus",
    "System",
    "SystemCategory",
    "AccessGrant",
    "AccessStatus",
    "RiskLevel",
    "OffboardingEvent",
    "OffboardingStatus",
    "AuditLogEntry",
]