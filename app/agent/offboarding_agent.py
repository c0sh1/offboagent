"""
Agente de offboarding basado en Claude con tool use.

Diferencia clave con OffboardingService (Fase 4): allí NOSOTROS
decidíamos la secuencia fija ("ordenar por riesgo, revocar todo").
Aquí es el LLM quien decide, turno a turno, qué herramienta llamar
y con qué argumentos, hasta considerar terminado el proceso -y
además redacta el informe final en lenguaje natural.

Seguimos controlando el "qué puede hacer" (las tools de tools.py);
el LLM solo controla el "en qué orden y cómo se explica".
"""
from sqlalchemy.orm import Session

from app.config import settings
from app.agent.llm_client import get_llm_client
from app.agent.tools import TOOLS_SCHEMA, ToolExecutor
from app.models import Person, OffboardingEvent

SYSTEM_PROMPT = """Eres un agente de seguridad encargado del offboarding de personas en una empresa.

Tu única tarea es: dado que una persona ha sido marcada para offboarding,
usa las herramientas disponibles para:
1. Listar sus accesos activos.
2. Revocar TODOS esos accesos, uno por uno, empezando siempre por los de
   riesgo 'critical', luego 'high', luego 'medium', luego 'low'.
3. Cuando ya no queden accesos activos, escribe un informe final breve,
   en español, dirigido a un responsable de seguridad/RR.HH., resumiendo
   qué se revocó, si algo falló y requiere intervención manual, y el
   nivel de riesgo que suponía cada sistema. No listes pasos técnicos
   de la API, sé claro y directo, máximo 150 palabras.

No inventes accesos ni sistemas que no te haya devuelto la herramienta
list_active_access_grants. Si una revocación falla, no te detengas:
continúa con el resto y menciónalo en el informe final.
"""

# Límite de turnos del bucle, por seguridad: evita que el agente quede
# atascado pidiendo herramientas indefinidamente si algo va mal.
_MAX_TURNS = 10


def run_offboarding_agent(db: Session, person: Person, event: OffboardingEvent) -> str:
    """Ejecuta el bucle de tool use y devuelve el informe final en texto."""
    client = get_llm_client()
    executor = ToolExecutor(db, person, event)

    messages = [
        {
            "role": "user",
            "content": (
                f"Persona a offboardear: {person.full_name} ({person.email}). "
                f"Motivo: {event.reason or 'no especificado'}."
            ),
        }
    ]

    for _ in range(_MAX_TURNS):
        response = client.messages.create(
            model=settings.llm_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS_SCHEMA,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return "".join(block.text for block in response.content if block.type == "text")

        # Puede haber varias llamadas a herramientas en la misma respuesta
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = executor.execute(block.name, block.input)
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": str(result)}
                )
        messages.append({"role": "user", "content": tool_results})

    return "El agente alcanzó el límite de turnos sin terminar. Revisa manualmente."