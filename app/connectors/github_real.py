"""
Conector REAL de GitHub: llamadas HTTP de verdad a la API de GitHub.

Con multi-tenancy: las credenciales (access_token, owner, repo) ya NO
se leen de settings/.env global - las pasa quien instancia el
conector (app/connectors/registry.py), descifradas desde la fila
System de la organización correspondiente.
"""
import httpx

from app.connectors.base import BaseConnector, ConnectorResult

GITHUB_API = "https://api.github.com"


class GitHubConnector(BaseConnector):
    connector_key = "github"

    def __init__(self, access_token: str, owner: str, repo: str):
        self.owner = owner
        self.repo = repo
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        url = f"{GITHUB_API}/repos/{self.owner}/{self.repo}/collaborators/{external_account_id}"
        try:
            response = httpx.delete(url, headers=self._headers, timeout=10)
        except httpx.HTTPError as e:
            return ConnectorResult(success=False, detail=f"Error de red: {e}")

        if response.status_code == 204:
            return ConnectorResult(
                success=True,
                detail=f"Colaborador '{external_account_id}' eliminado del repo {self.owner}/{self.repo}",
            )
        return ConnectorResult(
            success=False, detail=f"GitHub devolvió {response.status_code}: {response.text}"
        )

    def list_active_accounts(self) -> list[dict]:
        url = f"{GITHUB_API}/repos/{self.owner}/{self.repo}/collaborators"
        try:
            response = httpx.get(url, headers=self._headers, timeout=10)
        except httpx.HTTPError as e:
            print(f"[GitHubConnector] Error de red al listar colaboradores: {e}")
            return []

        if response.status_code != 200:
            print(f"[GitHubConnector] GitHub devolvió {response.status_code}: {response.text}")
            return []

        collaborators = response.json()
        return [
            {"external_account_id": c["login"], "email": f"{c['login']}@users.noreply.github.com"}
            for c in collaborators
        ]