"""
Script de prueba: crea las tablas y siembra datos de ejemplo
para verificar que el grafo de identidad funciona.

Ejecutar con: python scripts/init_db.py
"""
from app.models import (
    Base,
    engine,
    SessionLocal,
    Person,
    PersonType,
    PersonStatus,
    System,
    SystemCategory,
    AccessGrant,
    AccessStatus,
    RiskLevel,
)


def init_db():
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente.\n")


def seed_example_data():
    db = SessionLocal()
    try:
        # Evitar duplicar datos si el script se corre varias veces
        if db.query(Person).count() > 0:
            print("Ya hay datos de ejemplo. Saltando siembra.")
            return

        # 1. Creamos sistemas (nodos "herramienta")
        slack = System(name="Slack", category=SystemCategory.COMMUNICATION, connector_key="slack")
        github = System(name="GitHub", category=SystemCategory.CODE, connector_key="github")
        aws = System(name="AWS IAM", category=SystemCategory.CLOUD_INFRA, connector_key="aws_iam")
        db.add_all([slack, github, aws])
        db.flush()  # asigna IDs sin cerrar la transacción

        # 2. Creamos una persona (el contratista del caso real de r/sysadmin)
        contractor = Person(
            full_name="Carlos Mendez",
            email="carlos.mendez@contractor.example.com",
            person_type=PersonType.CONTRACTOR,
            status=PersonStatus.ACTIVE,
            department="Engineering",
        )
        db.add(contractor)
        db.flush()

        # 3. Creamos los accesos (las aristas del grafo)
        grants = [
            AccessGrant(
                person_id=contractor.id,
                system_id=slack.id,
                role="member",
                risk_level=RiskLevel.LOW,
                status=AccessStatus.ACTIVE,
            ),
            AccessGrant(
                person_id=contractor.id,
                system_id=github.id,
                role="write",
                risk_level=RiskLevel.MEDIUM,
                status=AccessStatus.ACTIVE,
            ),
            AccessGrant(
                person_id=contractor.id,
                system_id=aws.id,
                role="admin",  # <- este es el acceso peligroso del caso real (prod DB)
                risk_level=RiskLevel.CRITICAL,
                status=AccessStatus.ACTIVE,
            ),
        ]
        db.add_all(grants)
        db.commit()
        print(f"Persona creada: {contractor.full_name}")
        print(f"Accesos creados: {len(grants)}\n")

    finally:
        db.close()


def query_identity_graph():
    """Simula la pregunta clave: '¿qué accesos tiene esta persona?'"""
    db = SessionLocal()
    try:
        person = db.query(Person).filter(Person.full_name == "Carlos Mendez").first()
        print(f"--- Grafo de identidad de {person.full_name} ({person.status.value}) ---")
        for grant in person.access_grants:
            print(
                f"  -> {grant.system.name:12s} | rol: {grant.role:8s} | "
                f"riesgo: {grant.risk_level.value:8s} | estado: {grant.status.value}"
            )
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_example_data()
    query_identity_graph()