"""
Conector simulado (mock) de AWS IAM.

Este es el sistema más sensible del caso real (acceso admin a
producción), así que en la Fase 4 (servicio de offboarding) le
daremos prioridad de revocación más alta.
"""
from app.connectors.base import BaseConnector, ConnectorResult


class MockAWSIAMConnector(BaseConnector):
    connector_key = "aws_iam"

    def __init__(self, simulate_failure: bool = False):
        # simulate_failure nos permite forzar un fallo a propósito,
        # útil en la Fase 4 para probar cómo el sistema reacciona
        # cuando una revocación NO se puede completar automáticamente.
        self.simulate_failure = simulate_failure
        self._active_accounts = {
            "carlos.mendez@contractor.example.com": {"external_account_id": "AIDA_CARLOSMENDEZ"},
        }

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        # En la vida real: boto3 iam.delete_access_key / detach_user_policy / delete_login_profile
        if self.simulate_failure:
            print(f"[MockAWSIAM] ERROR al desactivar {external_account_id} (simulado)")
            return ConnectorResult(
                success=False,
                detail="No se pudo eliminar la política de IAM: permisos insuficientes (simulado)",
            )
        print(f"[MockAWSIAM] Desactivando usuario IAM {external_account_id}...")
        return ConnectorResult(success=True, detail="Usuario IAM desactivado (simulado)")

    def list_active_accounts(self) -> list[dict]:
        return [
            {"external_account_id": data["external_account_id"], "email": email}
            for email, data in self._active_accounts.items()
        ]