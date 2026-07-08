"""
Fábrica de conectores.

Con multi-tenancy, ya NO existe un conector "único" por tipo - cada
System (fila de la BD, propiedad de una Organization concreta) puede
tener sus propias credenciales cifradas.

get_connector_for_system(system) descifra esas credenciales (si las
hay) e instancia el conector real correspondiente; si no, cae al
conector simulado (mock) de ese mismo tipo.
"""
from app.connectors.base import BaseConnector
from app.connectors.mock_slack import MockSlackConnector
from app.connectors.mock_github import MockGitHubConnector
from app.connectors.mock_aws_iam import MockAWSIAMConnector
from app.connectors.mock_google_workspace import MockGoogleWorkspaceConnector
from app.connectors.mock_microsoft365 import MockMicrosoft365Connector
from app.connectors.mock_linear import MockLinearConnector
from app.connectors.mock_onepassword import MockOnePasswordConnector
from app.connectors.mock_okta import MockOktaConnector
from app.services.credentials_crypto import decrypt_credentials

CONNECTOR_TYPES = {
    "slack": {"label": "Slack", "category": "communication", "credential_fields": []},
    "github": {
        "label": "GitHub",
        "category": "code",
        "credential_fields": [
            {"key": "access_token", "label": "Personal Access Token", "secret": True},
            {"key": "owner", "label": "Usuario/Organización", "secret": False},
            {"key": "repo", "label": "Repositorio", "secret": False},
        ],
    },
    "aws_iam": {
        "label": "AWS IAM",
        "category": "cloud_infra",
        "credential_fields": [
            {"key": "access_key_id", "label": "Access Key ID", "secret": False},
            {"key": "secret_access_key", "label": "Secret Access Key", "secret": True},
            {"key": "region", "label": "Región", "secret": False},
        ],
    },
    "google_workspace": {"label": "Google Workspace", "category": "productivity", "credential_fields": []},
    "microsoft_365": {"label": "Microsoft 365", "category": "productivity", "credential_fields": []},
    "linear": {"label": "Linear", "category": "productivity", "credential_fields": []},
    "onepassword": {"label": "1Password", "category": "productivity", "credential_fields": []},
    "okta": {"label": "Okta", "category": "cloud_infra", "credential_fields": []},
}

_MOCK_CLASSES = {
    "slack": MockSlackConnector,
    "github": MockGitHubConnector,
    "aws_iam": MockAWSIAMConnector,
    "google_workspace": MockGoogleWorkspaceConnector,
    "microsoft_365": MockMicrosoft365Connector,
    "linear": MockLinearConnector,
    "onepassword": MockOnePasswordConnector,
    "okta": MockOktaConnector,
}


def get_connector_for_system(system) -> BaseConnector:
    if system.encrypted_credentials:
        creds = decrypt_credentials(system.encrypted_credentials)

        if system.connector_key == "github":
            from app.connectors.github_real import GitHubConnector
            return GitHubConnector(
                access_token=creds["access_token"], owner=creds["owner"], repo=creds["repo"]
            )

        if system.connector_key == "aws_iam":
            from app.connectors.aws_iam_real import AWSIAMConnector
            return AWSIAMConnector(
                access_key_id=creds["access_key_id"],
                secret_access_key=creds["secret_access_key"],
                region=creds.get("region", "us-east-1"),
            )

    mock_cls = _MOCK_CLASSES.get(system.connector_key)
    if mock_cls is None:
        raise ValueError(f"No hay conector disponible para '{system.connector_key}'")
    return mock_cls()