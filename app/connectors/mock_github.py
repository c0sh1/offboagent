"""
Conector simulado (mock) de GitHub.
"""
from app.connectors.base import BaseConnector, ConnectorResult


class MockGitHubConnector(BaseConnector):
    connector_key = "github"

    def __init__(self):
        self._active_accounts = {
            "carlos.mendez@contractor.example.com": {"external_account_id": "gh_carlosmendez"},
        }

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        # En la vida real: DELETE /orgs/{org}/members/{username} (API de GitHub)
        print(f"[MockGitHub] Eliminando de la organización a {external_account_id}...")
        return ConnectorResult(success=True, detail="Usuario eliminado de la organización (simulado)")

    def list_active_accounts(self) -> list[dict]:
        return [
            {"external_account_id": data["external_account_id"], "email": email}
            for email, data in self._active_accounts.items()
        ]