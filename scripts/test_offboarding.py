"""
Prueba end-to-end del servicio de offboarding.

Ejecutar con: python -m scripts.test_offboarding
"""
from app.models import SessionLocal, Person, AuditLogEntry
from app.services.offboarding_service import initiate_offboarding, execute_offboarding


def main():
    db = SessionLocal()
    try:
        person = db.query(Person).filter(Person.full_name == "Carlos Mendez").first()
        if person is None:
            print("No se encontró a Carlos Mendez. Ejecuta primero: python -m scripts.init_db")
            return

        print(f"Estado inicial de {person.full_name}: {person.status.value}\n")

        # 1. RR.HH. marca a la persona como offboarded
        event = initiate_offboarding(
            db,
            person_id=person.id,
            initiated_by="hr@empresa.com",
            reason="fin de contrato",
        )
        print(f"OffboardingEvent creado: {event.id} (estado: {event.status.value})\n")

        # 2. El agente ejecuta la revocación real
        event = execute_offboarding(db, event.id)

        print(f"Offboarding finalizado. Estado del evento: {event.status.value}")
        db.refresh(person)
        print(f"Estado final de la persona: {person.status.value}\n")

        print("--- Accesos tras el offboarding ---")
        for grant in person.access_grants:
            print(f"  {grant.system.name:12s} -> {grant.status.value}")

        print("\n--- Log de auditoría (para el informe SOC2/ISO27001) ---")
        logs = db.query(AuditLogEntry).filter(AuditLogEntry.offboarding_event_id == event.id).all()
        for log in logs:
            print(f"  [{log.timestamp}] {log.system_name:12s} | {log.action} -> {log.result} | {log.detail}")

    finally:
        db.close()


if __name__ == "__main__":
    main()