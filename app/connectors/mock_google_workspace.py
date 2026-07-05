"""
Conector simulado (mock) de Google Workspace.

Real: se integraría vía Admin SDK Directory API de Google, usando una
cuenta de servicio con "domain-wide delegation" autorizada por un
super admin del dominio. La acción real de revocación sería suspender
la cuenta (users.update con suspended=true), lo cual bloquea el acceso
a Gmail, Drive, Calendar, etc. de golpe.
"""
from app.connectors.base import BaseConnector, ConnectorResult


class MockGoogleWorkspaceConnector(BaseConnector):
    connector_key = "google_workspace"

    def __init__(self):
        self._active_accounts = {
            "carlos.mendez@contractor.example.com": {"external_account_id": "carlos.mendez"},
        }

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        print(f"[MockGoogleWorkspace] Suspendiendo cuenta {external_account_id}...")
        return ConnectorResult(success=True, detail="Cuenta suspendida en Google Workspace (simulado)")

    def list_active_accounts(self) -> list[dict]:
        return [
            {"external_account_id": data["external_account_id"], "email": email}
            for email, data in self._active_accounts.items()
        ]