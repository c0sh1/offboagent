"""
Prueba end-to-end del agente con Claude (tool use).

IMPORTANTE: necesitas una LLM_API_KEY real en tu .env
(consíguela en https://console.anthropic.com/settings/keys)

Ejecutar con: python -m scripts.test_agent
"""
from app.models import SessionLocal, Person, PersonStatus, AccessStatus, OffboardingEvent
from app.services.offboarding_service import initiate_offboarding
from app.agent.offboarding_agent import run_offboarding_agent


def main():
    db = SessionLocal()
    try:
        person = db.query(Person).filter(Person.full_name == "Carlos Mendez").first()
        if person is None:
            print("No se encontró a Carlos Mendez. Ejecuta primero: python -m scripts.init_db")
            return

        # Reseteamos su estado para poder repetir la prueba
        person.status = PersonStatus.ACTIVE
        for grant in person.access_grants:
            grant.status = AccessStatus.ACTIVE
            grant.revoked_at = None
        db.commit()

        event = initiate_offboarding(
            db, person.id, initiated_by="hr@empresa.com", reason="fin de contrato"
        )

        print("Ejecutando el agente (esto llama a la API de Claude)...\n")
        report = run_offboarding_agent(db, person, event)

        print("=" * 60)
        print("INFORME FINAL DEL AGENTE")
        print("=" * 60)
        print(report)
        print("=" * 60)

        # Guardamos el informe en el propio evento (para consultarlo luego)
        event = db.query(OffboardingEvent).filter(OffboardingEvent.id == event.id).first()
        event.summary_report = report
        db.commit()

        db.refresh(person)
        print("\n--- Estado final de los accesos ---")
        for grant in person.access_grants:
            print(f"  {grant.system.name:12s} -> {grant.status.value}")

    finally:
        db.close()


if __name__ == "__main__":
    main()