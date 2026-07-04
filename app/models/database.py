"""
Configuración de la base de datos con SQLAlchemy.

Aquí se define:
- `engine`: la conexión física a la base de datos (SQLite en el MVP)
- `SessionLocal`: una "fábrica" de sesiones (cada request/operación abre su propia sesión)
- `Base`: la clase de la que heredarán todos nuestros modelos (Person, System, etc.)
- `get_db`: función auxiliar para usar en FastAPI (dependency injection)
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# check_same_thread=False es necesario solo para SQLite (no aplica a Postgres/MySQL)
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Generador de sesión de base de datos.
    Se usará como dependencia en los endpoints de FastAPI (Fase 6),
    garantizando que la sesión se cierra siempre, incluso si hay un error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()