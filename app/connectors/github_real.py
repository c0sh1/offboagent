"""
Conector REAL de GitHub: llamadas HTTP de verdad a la API de GitHub.

Misma interfaz que MockGitHubConnector (BaseConnector) - esa es la
prueba de que el patrón Adapter funciona: el resto del sistema no
necesita saber si está hablando con el mock o con la API real.

Requiere en el .env:
    GITHUB_ACCESS_TOKEN, GITHUB_OWNER, GITHUB_REPO

Acción real que ejecuta:
- revoke_access: elimina a un colaborador de un repositorio concreto
  (DELETE /repos/{owner}/{repo}/collaborators/{username})
- list_active_accounts: lista los colaboradores actuales del repo
  (GET /repos/{owner}/{repo}/collaborators)

Nota de diseño honesta: la API de GitHub no siempre devuelve el email
real de un colaborador (por privacidad). Por eso aquí usamos el
username de GitHub como identificador, y solo generamos un email
"placeholder" para que el resto del sistema (que espera un email) no
falle. En un sistema de producción real, guardarías el username de
GitHub directamente en AccessGrant.external_account_id (que es
justamente para lo que existe ese campo) en vez de intentar
adivinarlo por email.
"""
import httpx

from app.connectors.base import BaseConnector, ConnectorResult
from app.config import settings

GITHUB_API = "https://api.github.com"


class GitHubConnector(BaseConnector):
    connector_key = "github"

    def __init__(self):
        self.owner = settings.github_owner
        self.repo = settings.github_repo
        self._headers = {
            "Authorization": f"Bearer {settings.github_access_token}",
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
            {
                "external_account_id": c["login"],
                "email": f"{c['login']}@users.noreply.github.com",  # placeholder, ver nota arriba
            }
            for c in collaborators
        ]