"""
Prueba de detección de accesos huérfanos.

Escenario: Carlos Mendez ya fue offboardeado (su Person.status es
OFFBOARDED), pero los sistemas externos (simulados) siguen
reportando su cuenta como activa -> exactamente el caso real del
contratista con acceso 3 meses después.

Ejecutar con: python -m scripts.test_orphan_detection
"""
from app.models import SessionLocal, Person, PersonStatus
from app.services.orphan_detection_service import detect_orphaned_access


def main():
    db = SessionLocal()
    try:
        person = db.query(Person).filter(Person.full_name == "Carlos Mendez").first()
        if person is None:
            print("No se encontró a Carlos Mendez. Ejecuta primero: python -m scripts.init_db")
            return

        print(f"Estado actual de {person.full_name}: {person.status.value}")
        if person.status != PersonStatus.OFFBOARDED:
            print("(Tip: ejecuta primero un offboarding real vía API o scripts.test_offboarding)")

        print("\nEjecutando detección de accesos huérfanos...\n")
        findings = detect_orphaned_access(db)

        if not findings:
            print("✅ No se detectaron accesos huérfanos.")
            return

        print(f"⚠️  Se detectaron {len(findings)} accesos huérfanos:\n")
        for f in findings:
            print(f"  Sistema: {f.system_name}")
            print(f"    Cuenta externa: {f.external_account_id} ({f.email})")
            print(f"    Motivo: {f.reason}")
            print(f"    Persona: {f.matched_person_id} | Grant: {f.matched_grant_id}\n")

    finally:
        db.close()


if __name__ == "__main__":
    main()