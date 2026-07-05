"""
Registro central de conectores.

Mapea connector_key (guardado en System.connector_key en la BD)
a una instancia del conector correspondiente.

Para GitHub: si hay credenciales reales configuradas en .env, se usa
el conector real (llamadas HTTP de verdad); si no, se cae de forma
automática al conector simulado. Así puedes seguir desarrollando y
probando sin romper nada, y "activas" la integración real solo
poniendo el token en el .env, sin tocar código.
"""
from app.config import settings
from app.connectors.base import BaseConnector
from app.connectors.mock_slack import MockSlackConnector
from app.connectors.mock_github import MockGitHubConnector
from app.connectors.mock_aws_iam import MockAWSIAMConnector


def _build_github_connector() -> BaseConnector:
    if settings.github_access_token and settings.github_owner and settings.github_repo:
        from app.connectors.github_real import GitHubConnector
        return GitHubConnector()
    return MockGitHubConnector()


_CONNECTOR_REGISTRY: dict[str, BaseConnector] = {
    "slack": MockSlackConnector(),
    "github": _build_github_connector(),
    "aws_iam": MockAWSIAMConnector(),
}


def get_connector(connector_key: str) -> BaseConnector:
    connector = _CONNECTOR_REGISTRY.get(connector_key)
    if connector is None:
        raise ValueError(f"No hay conector registrado para la clave '{connector_key}'")
    return connector