"""
Conector REAL de AWS IAM, usando boto3.

A diferencia de GitHub (donde "revocar" es una sola llamada DELETE),
en IAM no existe un único botón de "desactivar a esta persona".
Revocar de verdad significa despojar al usuario de TODO lo que le
daría acceso, en varios pasos:

1. Eliminar sus access keys (credenciales programáticas / CLI / SDK)
2. Eliminar su login profile (acceso a la consola web con contraseña)
3. Desvincular sus políticas administradas (permisos "adjuntados")
4. Eliminar sus políticas inline (permisos escritos directamente en el usuario)

Nota importante: esto NO elimina el usuario IAM en sí (por diseño:
mantenemos el registro/nombre para auditoría), solo le quita todo
lo que le permitiría hacer algo. Si quisieras eliminar el usuario
por completo, sería un paso adicional explícito, no automático.

⚠️  ADVERTENCIA: prueba esto SIEMPRE con una cuenta de AWS de pruebas
y un usuario IAM creado específicamente para practicar, nunca con
una cuenta de producción real.
"""
import boto3
from botocore.exceptions import ClientError

from app.connectors.base import BaseConnector, ConnectorResult
from app.config import settings


class AWSIAMConnector(BaseConnector):
    connector_key = "aws_iam"

    def __init__(self):
        self._client = boto3.client(
            "iam",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )

    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        username = external_account_id
        actions_done: list[str] = []

        try:
            # 1. Access keys (credenciales programáticas)
            keys = self._client.list_access_keys(UserName=username)["AccessKeyMetadata"]
            for key in keys:
                self._client.delete_access_key(UserName=username, AccessKeyId=key["AccessKeyId"])
                actions_done.append(f"access key {key['AccessKeyId']} eliminada")

            # 2. Login profile (contraseña de consola)
            try:
                self._client.delete_login_profile(UserName=username)
                actions_done.append("perfil de consola eliminado")
            except ClientError as e:
                if e.response["Error"]["Code"] != "NoSuchEntity":
                    raise

            # 3. Políticas administradas (adjuntadas)
            attached = self._client.list_attached_user_policies(UserName=username)["AttachedPolicies"]
            for policy in attached:
                self._client.detach_user_policy(UserName=username, PolicyArn=policy["PolicyArn"])
                actions_done.append(f"política '{policy['PolicyName']}' desvinculada")

            # 4. Políticas inline (escritas directamente en el usuario)
            inline = self._client.list_user_policies(UserName=username)["PolicyNames"]
            for policy_name in inline:
                self._client.delete_user_policy(UserName=username, PolicyName=policy_name)
                actions_done.append(f"política inline '{policy_name}' eliminada")

        except ClientError as e:
            return ConnectorResult(success=False, detail=f"Error de AWS IAM: {e}")

        if not actions_done:
            return ConnectorResult(
                success=True, detail=f"'{username}' no tenía credenciales/permisos activos que revocar"
            )
        return ConnectorResult(success=True, detail="; ".join(actions_done))

    def list_active_accounts(self) -> list[dict]:
        try:
            users = self._client.list_users()["Users"]
        except ClientError as e:
            print(f"[AWSIAMConnector] Error al listar usuarios: {e}")
            return []

        active_accounts = []
        for user in users:
            username = user["UserName"]
            has_keys = len(
                self._client.list_access_keys(UserName=username)["AccessKeyMetadata"]
            ) > 0
            has_login = self._has_login_profile(username)
            has_policies = len(
                self._client.list_attached_user_policies(UserName=username)["AttachedPolicies"]
            ) > 0

            if has_keys or has_login or has_policies:
                active_accounts.append(
                    {
                        "external_account_id": username,
                        # AWS IAM no tiene un campo "email" nativo; usamos un
                        # placeholder, igual que documentamos en github_real.py.
                        # En producción, guardaríamos el username directamente
                        # en AccessGrant.external_account_id.
                        "email": f"{username}@aws-iam.local",
                    }
                )
        return active_accounts

    def _has_login_profile(self, username: str) -> bool:
        try:
            self._client.get_login_profile(UserName=username)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                return False
            raise