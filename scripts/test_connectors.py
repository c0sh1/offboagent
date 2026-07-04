"""
Script de prueba: recorre los accesos de Carlos Mendez (creado en la
Fase 2) y llama al conector correspondiente de cada uno, SIN que este
código sepa nada de Slack/GitHub/AWS en concreto. Esa es la prueba
real de que el patrón Adapter funciona.

Ejecutar con: python -m scripts.test_connectors
"""
from app.models import SessionLocal, Person
from app.connectors.registry import get_connector


def main():
    db = SessionLocal()
    try:
        person = db.query(Person).filter(Person.full_name == "Carlos Mendez").first()
        if person is None:
            print("No se encontró a Carlos Mendez. Ejecuta primero: python -m scripts.init_db")
            return

        print(f"Probando conectores para los accesos de {person.full_name}...\n")

        for grant in person.access_grants:
            system = grant.system
            # Aquí está la magia del patrón Adapter: el código no sabe
            # si connector_key es "slack", "github" o "aws_iam".
            connector = get_connector(system.connector_key)
            result = connector.revoke_access(external_account_id="dummy-id-123")
            estado = "✅ OK" if result.success else "❌ FALLÓ"
            print(f"  {system.name:12s} -> {estado} | {result.detail}")

    finally:
        db.close()


if __name__ == "__main__":
    main()