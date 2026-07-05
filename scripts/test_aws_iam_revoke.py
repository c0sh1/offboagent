"""
Prueba de revocación REAL en AWS IAM.

⚠️  CUIDADO: esto elimina de verdad las access keys, el login profile
y todas las políticas (administradas + inline) de un usuario IAM real.
Pide confirmación explícita antes de ejecutar. Usa SIEMPRE una cuenta
de AWS de pruebas, con un usuario IAM creado específicamente para
practicar esto - nunca una cuenta de producción real.

Ejecutar con: python -m scripts.test_aws_iam_revoke <username>
"""
import sys

from app.connectors.aws_iam_real import AWSIAMConnector


def main():
    if len(sys.argv) < 2:
        print("Uso: python -m scripts.test_aws_iam_revoke <username_iam_a_revocar>")
        return

    username = sys.argv[1]
    connector = AWSIAMConnector()

    confirm = input(
        f"¿Seguro que quieres revocar TODOS los accesos del usuario IAM '{username}'? "
        f"Esto es IRREVERSIBLE. Escribe 'si' para confirmar: "
    )
    if confirm.strip().lower() != "si":
        print("Cancelado.")
        return

    result = connector.revoke_access(username)
    print("✅ Éxito:" if result.success else "❌ Falló:", result.detail)


if __name__ == "__main__":
    main()