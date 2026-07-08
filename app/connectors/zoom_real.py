"""
Conector REAL de Zoom, vía Server-to-Server OAuth.
"""
import base64

import httpx

from app.connectors.base import BaseConnector, ConnectorResult

_ZOOM_API = "https://api.zoom.us/v2"


class ZoomConnector(BaseConnector):
    connector_key = "zoom"

    def __init__(self, account_id: str, client_id: str, client_secret: str):
        self.account_id = account_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: str | None = None

    def _get_access_token(self) -> str:
        if self._token:
            return self._token

        credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        response = httpx.post(
            "https://zoom.us/oauth/token",
            headers={"Authorization": f"Basic {credentials}"},
            params={"grant_type": "account_credentials", "account_id": self.account_id},
            timeout=10,
        )
        response.raise_for_status()
        self._token = response.json()["access_token"]
        return self._token

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        try:
            headers = {"Authorization": f"Bearer {self._get_access_token()}"}
        except Exception as e:
            return ConnectorResult(success=False, detail=f"Error de autenticación: {e}")

        try:
            response = httpx.put(
                f"{_ZOOM_API}/users/{external_account_id}/status",
                headers=headers,
                json={"action": "deactivate"},
                timeout=10,
            )
        except httpx.HTTPError as e:
            return ConnectorResult(success=False, detail=f"Error de red: {e}")

        if response.status_code in (200, 204):
            return ConnectorResult(
                success=True, detail=f"Usuario '{external_account_id}' desactivado en Zoom"
            )
        return ConnectorResult(success=False, detail=f"Zoom devolvió {response.status_code}: {response.text}")

    def list_active_accounts(self) -> list[dict]:
        try:
            headers = {"Authorization": f"Bearer {self._get_access_token()}"}
        except Exception as e:
            print(f"[ZoomConnector] Error de autenticación: {e}")
            return []

        try:
            response = httpx.get(
                f"{_ZOOM_API}/users", headers=headers, params={"status": "active"}, timeout=10
            )
        except httpx.HTTPError as e:
            print(f"[ZoomConnector] Error de red: {e}")
            return []

        if response.status_code != 200:
            print(f"[ZoomConnector] Zoom devolvió {response.status_code}: {response.text}")
            return []

        users = response.json().get("users", [])
        return [{"external_account_id": u["id"], "email": u["email"]} for u in users]