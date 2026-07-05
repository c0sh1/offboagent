"""
Conector simulado (mock) de Okta.

Nota curiosa de producto: Okta es en sí mismo un competidor directo
(Okta Lifecycle Management es una de las soluciones enterprise que
mencionamos al inicio). Pero muchas empresas medianas usan Okta SOLO
como Identity Provider (SSO) sin pagar por el módulo de Lifecycle
Management completo - ahí es exactamente donde nuestro producto
encaja: cubrimos la orquestación de offboarding que Okta básico no
incluye.

Real: Okta tiene una API REST bien documentada. La revocación real
sería desactivar al usuario (POST /api/v1/users/{id}/lifecycle/deactivate).
"""
from app.connectors.base import BaseConnector, ConnectorResult


class MockOktaConnector(BaseConnector):
    connector_key = "okta"

    def __init__(self):
        self._active_accounts = {
            "carlos.mendez@contractor.example.com": {"external_account_id": "00u_carlosmendez"},
        }

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        print(f"[MockOkta] Desactivando usuario {external_account_id}...")
        return ConnectorResult(success=True, detail="Usuario desactivado en Okta (simulado)")

    def list_active_accounts(self) -> list[dict]:
        return [
            {"external_account_id": data["external_account_id"], "email": email}
            for email, data in self._active_accounts.items()
        ]