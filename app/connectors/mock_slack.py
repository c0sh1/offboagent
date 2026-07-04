"""
Conector simulado (mock) de Slack.

Se comporta como el conector real (misma interfaz), pero en vez de
llamar a la API real de Slack, simula la respuesta. Útil para
desarrollar y probar todo el flujo de offboarding sin necesitar
credenciales reales todavía.

Cuando construyamos el conector real, solo cambiaremos el CUERPO
de estos métodos (llamada HTTP real vía httpx a la API de Slack),
la interfaz (BaseConnector) se mantiene igual.
"""
from app.connectors.base import BaseConnector, ConnectorResult


class MockSlackConnector(BaseConnector):
    connector_key = "slack"

    def __init__(self):
        # Simula una "base de datos" de cuentas activas en Slack
        self._active_accounts = {
            "carlos.mendez@contractor.example.com": {"external_account_id": "U001CARLOS"},
        }

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        # Simulación: en la vida real aquí iría una llamada a
        # https://api.slack.com/methods/admin.users.remove
        print(f"[MockSlack] Desactivando cuenta {external_account_id}...")
        return ConnectorResult(success=True, detail="Usuario desactivado en Slack (simulado)")

    def list_active_accounts(self) -> list[dict]:
        return [
            {"external_account_id": data["external_account_id"], "email": email}
            for email, data in self._active_accounts.items()
        ]