"""
Script de inicialización: crea las tablas de la base de datos.

Con multi-tenancy, ya NO sembramos datos de ejemplo aquí: cualquier
Person/System que creáramos sin un Usuario/Organization real
asociado quedaría inaccesible (huérfano). Cada empresa crea sus
propios datos, empezando por registrar su organización desde el
frontend (o vía POST /auth/register-organization).

Ejecutar con: python -m scripts.init_db
"""
from app.models import Base, engine


def init_db():
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente.")
    print("\nSiguiente paso: registra tu primera empresa desde el frontend")
    print("(o vía POST /auth/register-organization) para crear tu usuario Owner.")


if __name__ == "__main__":
    init_db()