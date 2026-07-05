"""
Definición de las "tools" (herramientas) que el agente de Claude puede
usar durante un offboarding, y el ToolExecutor que las ejecuta de verdad.

Patrón de tool use: le decimos al modelo QUÉ herramientas existen
(nombre + esquema de sus parámetros en TOOLS_SCHEMA) y él decide
CUÁNDO y CON QUÉ argumentos llamarlas. Nosotros seguimos controlando
al 100% qué hace cada herramienta por dentro (ToolExecutor).

Detalle de seguridad importante: el LLM NUNCA recibe ni puede inventar
un person_id libremente. ToolExecutor está atado a una persona/evento
concretos que NOSOTROS fijamos antes de empezar (ver offboarding_agent.py).
El modelo solo puede operar dentro de ese ámbito.
"""
from sqlalchemy.orm import Session

from app.models import Person, AccessStatus, OffboardingEvent
from app.services.offboarding_service import revoke_grant_by_id

TOOLS_SCHEMA = [
    {
        "name": "list_active_access_grants",
        "description": (
            "Devuelve todos los accesos ACTIVOS de la persona que se está "
            "offboardeando: sistema, rol y nivel de riesgo. Úsala primero, "
            "antes de revocar nada, para saber qué hay que hacer."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "revoke_access_grant",
        "description": (
            "Revoca un acceso concreto (identificado por grant_id) a través "
            "del conector del sistema correspondiente, y deja constancia en "
            "el log de auditoría. Revoca siempre primero los accesos de "
            "riesgo 'critical' y 'high' antes que los de 'medium' o 'low'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "grant_id": {
                    "type": "string",
                    "description": "El id del AccessGrant a revocar (obtenido de list_active_access_grants).",
                }
            },
            "required": ["grant_id"],
        },
    },
]


class ToolExecutor:
    """Ata las tools genéricas a una persona y un evento concretos."""

    def __init__(self, db: Session, person: Person, event: OffboardingEvent):
        self.db = db
        self.person = person
        self.event = event

    def execute(self, tool_name: str, tool_input: dict) -> dict:
        if tool_name == "list_active_access_grants":
            return self._list_active_access_grants()
        if tool_name == "revoke_access_grant":
            return revoke_grant_by_id(self.db, self.event, tool_input["grant_id"])
        return {"error": f"Herramienta desconocida: {tool_name}"}

    def _list_active_access_grants(self) -> dict:
        self.db.refresh(self.person)
        grants = [g for g in self.person.access_grants if g.status == AccessStatus.ACTIVE]
        return {
            "access_grants": [
                {
                    "grant_id": g.id,
                    "system": g.system.name,
                    "role": g.role,
                    "risk_level": g.risk_level.value,
                }
                for g in grants
            ]
        }