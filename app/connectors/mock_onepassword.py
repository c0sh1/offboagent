"""
Conector simulado (mock) de 1Password.

Este es de los más críticos en cualquier offboarding real: un gestor
de contraseñas con acceso vivo es de máximo riesgo (acceso indirecto
a TODO lo demás guardado ahí).

Real: 1Password tiene una API SCIM Bridge para Business/Enterprise
(similar al patrón que vimos con Notion). La acción real sería
suspender al usuario vía esa API.
"""
from app.connectors.base import BaseConnector, ConnectorResult


class MockOnePasswordConnector(BaseConnector):
    connector_key = "onepassword"

    def __init__(self):
        self._active_accounts = {
            "carlos.mendez@contractor.example.com": {"external_account_id": "carlos.mendez"},
        }

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        print(f"[MockOnePassword] Suspendiendo cuenta {external_account_id}...")
        return ConnectorResult(success=True, detail="Cuenta suspendida en 1Password (simulado)")

    def list_active_accounts(self) -> list[dict]:
        return [
            {"external_account_id": data["external_account_id"], "email": email}
            for email, data in self._active_accounts.items()
        ]