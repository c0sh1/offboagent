"""
Conector REAL de Microsoft 365, vía Microsoft Graph API.
"""
import httpx

from app.connectors.base import BaseConnector, ConnectorResult

_GRAPH_API = "https://graph.microsoft.com/v1.0"


class Microsoft365Connector(BaseConnector):
    connector_key = "microsoft_365"

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: str | None = None

    def _get_access_token(self) -> str:
        if self._token:
            return self._token

        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }
        response = httpx.post(url, data=data, timeout=10)
        response.raise_for_status()
        self._token = response.json()["access_token"]
        return self._token

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        try:
            headers = {"Authorization": f"Bearer {self._get_access_token()}"}
        except Exception as e:
            return ConnectorResult(success=False, detail=f"Error de autenticación: {e}")

        try:
            disable_resp = httpx.patch(
                f"{_GRAPH_API}/users/{external_account_id}",
                headers=headers,
                json={"accountEnabled": False},
                timeout=10,
            )
        except httpx.HTTPError as e:
            return ConnectorResult(success=False, detail=f"Error de red: {e}")

        if disable_resp.status_code not in (200, 204):
            return ConnectorResult(
                success=False,
                detail=f"Microsoft Graph devolvió {disable_resp.status_code}: {disable_resp.text}",
            )

        try:
            revoke_resp = httpx.post(
                f"{_GRAPH_API}/users/{external_account_id}/revokeSignInSessions",
                headers=headers,
                timeout=10,
            )
        except httpx.HTTPError as e:
            return ConnectorResult(
                success=True,
                detail=f"Cuenta deshabilitada, pero no se pudieron revocar las sesiones activas: {e}",
            )

        if revoke_resp.status_code not in (200, 204):
            return ConnectorResult(
                success=True,
                detail=f"Cuenta deshabilitada; aviso al revocar sesiones: {revoke_resp.status_code}",
            )

        return ConnectorResult(
            success=True, detail="Cuenta deshabilitada y sesiones activas revocadas en Microsoft 365"
        )

    def list_active_accounts(self) -> list[dict]:
        try:
            headers = {"Authorization": f"Bearer {self._get_access_token()}"}
        except Exception as e:
            print(f"[Microsoft365Connector] Error de autenticación: {e}")
            return []

        try:
            response = httpx.get(
                f"{_GRAPH_API}/users",
                headers=headers,
                params={"$select": "id,userPrincipalName,mail,accountEnabled"},
                timeout=10,
            )
        except httpx.HTTPError as e:
            print(f"[Microsoft365Connector] Error de red: {e}")
            return []

        if response.status_code != 200:
            print(f"[Microsoft365Connector] Microsoft Graph devolvió {response.status_code}: {response.text}")
            return []

        users = response.json().get("value", [])
        return [
            {"external_account_id": u["id"], "email": u.get("mail") or u.get("userPrincipalName")}
            for u in users
            if u.get("accountEnabled")
        ]