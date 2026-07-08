"""
Fábrica de conectores.

get_connector_for_system(system) descifra las credenciales de ESE
System concreto (si las hay) e instancia el conector real
correspondiente; si no, cae al conector simulado (mock) de ese
mismo tipo.
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
from app.connectors.mock_zoom import MockZoomConnector
from app.services.credentials_crypto import decrypt_credentials

CONNECTOR_TYPES = {
    "slack": {
        "label": "Slack",
        "category": "communication",
        "credential_fields": [],
    },
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
    "google_workspace": {
        "label": "Google Workspace",
        "category": "productivity",
        "credential_fields": [
            {
                "key": "service_account_json",
                "label": "Contenido del JSON de la cuenta de servicio",
                "secret": True,
            },
            {"key": "admin_email", "label": "Email de un Super Admin", "secret": False},
            {"key": "domain", "label": "Dominio (opcional)", "secret": False},
        ],
    },
    "microsoft_365": {
        "label": "Microsoft 365",
        "category": "productivity",
        "credential_fields": [
            {"key": "tenant_id", "label": "Tenant ID", "secret": False},
            {"key": "client_id", "label": "Client ID", "secret": False},
            {"key": "client_secret", "label": "Client Secret", "secret": True},
        ],
    },
    "linear": {"label": "Linear", "category": "productivity", "credential_fields": []},
    "onepassword": {"label": "1Password", "category": "productivity", "credential_fields": []},
    "okta": {"label": "Okta", "category": "cloud_infra", "credential_fields": []},
    "zoom": {
        "label": "Zoom",
        "category": "communication",
        "credential_fields": [
            {"key": "account_id", "label": "Account ID", "secret": False},
            {"key": "client_id", "label": "Client ID", "secret": False},
            {"key": "client_secret", "label": "Client Secret", "secret": True},
        ],
    },
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
    "zoom": MockZoomConnector,
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

        if system.connector_key == "google_workspace":
            from app.connectors.google_workspace_real import GoogleWorkspaceConnector
            return GoogleWorkspaceConnector(
                service_account_json=creds["service_account_json"],
                admin_email=creds["admin_email"],
                domain=creds.get("domain", ""),
            )

        if system.connector_key == "microsoft_365":
            from app.connectors.microsoft365_real import Microsoft365Connector
            return Microsoft365Connector(
                tenant_id=creds["tenant_id"],
                client_id=creds["client_id"],
                client_secret=creds["client_secret"],
            )

        if system.connector_key == "zoom":
            from app.connectors.zoom_real import ZoomConnector
            return ZoomConnector(
                account_id=creds["account_id"],
                client_id=creds["client_id"],
                client_secret=creds["client_secret"],
            )

    mock_cls = _MOCK_CLASSES.get(system.connector_key)
    if mock_cls is None:
        raise ValueError(f"No hay conector disponible para '{system.connector_key}'")
    return mock_cls()