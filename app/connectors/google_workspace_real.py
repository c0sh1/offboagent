"""
Conector REAL de Google Workspace, vía Admin SDK Directory API.

Requiere una cuenta de servicio (Service Account) de Google Cloud con
"domain-wide delegation" habilitada y autorizada en el Admin Console
de Google Workspace, con el scope:
    https://www.googleapis.com/auth/admin.directory.user
"""
import json

import httpx
from google.oauth2 import service_account
import google.auth.transport.requests

from app.connectors.base import BaseConnector, ConnectorResult

_SCOPES = ["https://www.googleapis.com/auth/admin.directory.user"]
_API_BASE = "https://admin.googleapis.com/admin/directory/v1"


class GoogleWorkspaceConnector(BaseConnector):
    connector_key = "google_workspace"

    def __init__(self, service_account_json: str, admin_email: str, domain: str = ""):
        self.domain = domain
        info = json.loads(service_account_json)
        credentials = service_account.Credentials.from_service_account_info(info, scopes=_SCOPES)
        self._credentials = credentials.with_subject(admin_email)

    def _get_access_token(self) -> str:
        request = google.auth.transport.requests.Request()
        self._credentials.refresh(request)
        return self._credentials.token

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        try:
            token = self._get_access_token()
        except Exception as e:
            return ConnectorResult(success=False, detail=f"Error de autenticación: {e}")

        url = f"{_API_BASE}/users/{external_account_id}"
        try:
            response = httpx.patch(
                url, headers={"Authorization": f"Bearer {token}"}, json={"suspended": True}, timeout=10
            )
        except httpx.HTTPError as e:
            return ConnectorResult(success=False, detail=f"Error de red: {e}")

        if response.status_code == 200:
            return ConnectorResult(
                success=True, detail=f"Cuenta '{external_account_id}' suspendida en Google Workspace"
            )
        return ConnectorResult(
            success=False, detail=f"Google devolvió {response.status_code}: {response.text}"
        )

    def list_active_accounts(self) -> list[dict]:
        try:
            token = self._get_access_token()
        except Exception as e:
            print(f"[GoogleWorkspaceConnector] Error de autenticación: {e}")
            return []

        params = {"domain": self.domain} if self.domain else {"customer": "my_customer"}
        try:
            response = httpx.get(
                f"{_API_BASE}/users",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=10,
            )
        except httpx.HTTPError as e:
            print(f"[GoogleWorkspaceConnector] Error de red: {e}")
            return []

        if response.status_code != 200:
            print(f"[GoogleWorkspaceConnector] Google devolvió {response.status_code}: {response.text}")
            return []

        users = response.json().get("users", [])
        return [
            {"external_account_id": u["primaryEmail"], "email": u["primaryEmail"]}
            for u in users
            if not u.get("suspended", False)
        ]