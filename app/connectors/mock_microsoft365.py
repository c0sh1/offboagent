"""
Conector simulado (mock) de Microsoft 365.

Real: se integraría vía Microsoft Graph API, con una app registrada
en Azure AD usando permisos de tipo "Application" (no "Delegated") y
consentimiento de administrador. La revocación real sería un PATCH a
/users/{id} con accountEnabled=false, más una llamada a
/users/{id}/revokeSignInSessions para invalidar sesiones activas.
"""
from app.connectors.base import BaseConnector, ConnectorResult


class MockMicrosoft365Connector(BaseConnector):
    connector_key = "microsoft_365"

    def __init__(self):
        self._active_accounts = {
            "carlos.mendez@contractor.example.com": {"external_account_id": "carlos.mendez"},
        }

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        print(f"[MockMicrosoft365] Deshabilitando cuenta {external_account_id} y revocando sesiones...")
        return ConnectorResult(
            success=True, detail="Cuenta deshabilitada y sesiones revocadas en M365 (simulado)"
        )

    def list_active_accounts(self) -> list[dict]:
        return [
            {"external_account_id": data["external_account_id"], "email": email}
            for email, data in self._active_accounts.items()
        ]