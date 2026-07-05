"""
Registro central de conectores.

Mapea connector_key (guardado en System.connector_key en la BD)
a una instancia del conector correspondiente.

GitHub y AWS IAM: si hay credenciales reales configuradas en .env, se
usa el conector real; si no, se cae de forma automática al conector
simulado. Google Workspace, Microsoft 365, Linear, 1Password y Okta
se quedan en modo simulado por ahora (mismo patrón, listos para
convertirse en reales el día que se conecten credenciales de verdad).
"""
from app.config import settings
from app.connectors.base import BaseConnector
from app.connectors.mock_slack import MockSlackConnector
from app.connectors.mock_github import MockGitHubConnector
from app.connectors.mock_aws_iam import MockAWSIAMConnector
from app.connectors.mock_google_workspace import MockGoogleWorkspaceConnector
from app.connectors.mock_microsoft365 import MockMicrosoft365Connector
from app.connectors.mock_linear import MockLinearConnector
from app.connectors.mock_onepassword import MockOnePasswordConnector
from app.connectors.mock_okta import MockOktaConnector


def _build_github_connector() -> BaseConnector:
    if settings.github_access_token and settings.github_owner and settings.github_repo:
        from app.connectors.github_real import GitHubConnector
        return GitHubConnector()
    return MockGitHubConnector()


def _build_aws_iam_connector() -> BaseConnector:
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        from app.connectors.aws_iam_real import AWSIAMConnector
        return AWSIAMConnector()
    return MockAWSIAMConnector()


_CONNECTOR_REGISTRY: dict[str, BaseConnector] = {
    "slack": MockSlackConnector(),
    "github": _build_github_connector(),
    "aws_iam": _build_aws_iam_connector(),
    "google_workspace": MockGoogleWorkspaceConnector(),
    "microsoft_365": MockMicrosoft365Connector(),
    "linear": MockLinearConnector(),
    "onepassword": MockOnePasswordConnector(),
    "okta": MockOktaConnector(),
}


def get_connector(connector_key: str) -> BaseConnector:
    connector = _CONNECTOR_REGISTRY.get(connector_key)
    if connector is None:
        raise ValueError(f"No hay conector registrado para la clave '{connector_key}'")
    return connector