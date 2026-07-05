"""
Prueba del conector REAL de AWS IAM (solo lectura, no revoca nada).

⚠️  Usa una cuenta de AWS de pruebas, nunca una de producción.

Requiere en tu .env:
    AWS_ACCESS_KEY_ID=...
    AWS_SECRET_ACCESS_KEY=...
    AWS_REGION=us-east-1  (o la que uses)

Ejecutar con: python -m scripts.test_aws_iam_real
"""
from app.connectors.aws_iam_real import AWSIAMConnector


def main():
    connector = AWSIAMConnector()

    print("Listando usuarios IAM con accesos activos...\n")
    accounts = connector.list_active_accounts()

    if not accounts:
        print("No se encontraron usuarios IAM con accesos activos (o hubo un error).")
        return

    for acc in accounts:
        print(f"  - {acc['external_account_id']}")

    print("\nEste script es de SOLO LECTURA, no ha revocado nada.")
    print("Para probar una revocación real: python -m scripts.test_aws_iam_revoke <username>")


if __name__ == "__main__":
    main()