"""
Conector simulado (mock) de Linear (gestión de proyectos/tickets).

Real: Linear tiene una API GraphQL. La revocación real sería una
mutation para eliminar al miembro del workspace/equipo.
"""
from app.connectors.base import BaseConnector, ConnectorResult


class MockLinearConnector(BaseConnector):
    connector_key = "linear"

    def __init__(self):
        self._active_accounts = {
            "carlos.mendez@contractor.example.com": {"external_account_id": "carlos-mendez-linear"},
        }

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        print(f"[MockLinear] Eliminando del workspace a {external_account_id}...")
        return ConnectorResult(success=True, detail="Usuario eliminado del workspace de Linear (simulado)")

    def list_active_accounts(self) -> list[dict]:
        return [
            {"external_account_id": data["external_account_id"], "email": email}
            for email, data in self._active_accounts.items()
        ]