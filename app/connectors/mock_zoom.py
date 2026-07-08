"""
Conector simulado (mock) de Zoom. Empieza sin cuentas de ejemplo
fijas (a diferencia de los mocks originales), para no repetir la
confusión de la Fase de multi-tenancy.
"""
from app.connectors.base import BaseConnector, ConnectorResult


class MockZoomConnector(BaseConnector):
    connector_key = "zoom"

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        print(f"[MockZoom] Desactivando usuario {external_account_id}...")
        return ConnectorResult(success=True, detail="Usuario desactivado en Zoom (simulado)")

    def list_active_accounts(self) -> list[dict]:
        return []