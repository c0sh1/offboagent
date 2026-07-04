"""
Prueba del caso de FALLO: simula que AWS IAM no puede revocar el
acceso (ej. permisos insuficientes de la cuenta de servicio), y
verifica que el sistema lo captura correctamente en vez de fallar
en silencio o marcar todo como "éxito".

Ejecutar con: python -m scripts.test_offboarding_failure
"""
from app.models import SessionLocal, Person, PersonStatus, AccessStatus, AuditLogEntry
import app.connectors.registry as registry
from app.connectors.mock_aws_iam import MockAWSIAMConnector
from app.services.offboarding_service import initiate_offboarding, execute_offboarding


def main():
    # Forzamos que el conector de AWS falle, simulando un problema real
    registry._CONNECTOR_REGISTRY["aws_iam"] = MockAWSIAMConnector(simulate_failure=True)

    db = SessionLocal()
    try:
        person = db.query(Person).filter(Person.full_name == "Carlos Mendez").first()

        # Reseteamos su estado para poder repetir la prueba
        person.status = PersonStatus.ACTIVE
        for grant in person.access_grants:
            grant.status = AccessStatus.ACTIVE
            grant.revoked_at = None
        db.commit()

        event = initiate_offboarding(db, person.id, initiated_by="hr@empresa.com", reason="despido")
        event = execute_offboarding(db, event.id)

        print(f"Estado del evento: {event.status.value}  <- debe ser 'completed_with_errors'\n")

        db.refresh(person)
        for grant in person.access_grants:
            print(f"  {grant.system.name:12s} -> {grant.status.value}")

        print("\n--- Log de auditoría ---")
        logs = db.query(AuditLogEntry).filter(AuditLogEntry.offboarding_event_id == event.id).all()
        for log in logs:
            marca = "⚠️ " if log.result == "failed" else "✅ "
            print(f"  {marca}{log.system_name:12s} -> {log.result} | {log.detail}")

    finally:
        db.close()


if __name__ == "__main__":
    main()