"""
Registro central de conectores.

Mapea connector_key (guardado en System.connector_key en la BD)
a una instancia del conector correspondiente.

Esto es lo que hace posible que el servicio de offboarding (Fase 4)
escriba código genérico como:

    connector = get_connector(system.connector_key)
    connector.revoke_access(external_account_id)

sin ningún "if system.name == 'Slack'" hardcodeado.
Cuando en el futuro sustituyamos un mock por el conector real,
solo cambiamos esta línea (una sola vez, en un solo lugar).
"""
from app.connectors.base import BaseConnector
from app.connectors.mock_slack import MockSlackConnector
from app.connectors.mock_github import MockGitHubConnector
from app.connectors.mock_aws_iam import MockAWSIAMConnector

_CONNECTOR_REGISTRY: dict[str, BaseConnector] = {
    "slack": MockSlackConnector(),
    "github": MockGitHubConnector(),
    "aws_iam": MockAWSIAMConnector(),
}


def get_connector(connector_key: str) -> BaseConnector:
    connector = _CONNECTOR_REGISTRY.get(connector_key)
    if connector is None:
        raise ValueError(f"No hay conector registrado para la clave '{connector_key}'")
    return connector