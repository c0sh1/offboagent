"""
Prueba del conector REAL de GitHub (solo lectura, no revoca nada).

Requiere en tu .env:
    GITHUB_ACCESS_TOKEN=github_pat_...
    GITHUB_OWNER=tu-usuario-de-github
    GITHUB_REPO=nombre-de-tu-repo-de-prueba

Ejecutar con: python -m scripts.test_github_real
"""
from app.connectors.github_real import GitHubConnector


def main():
    connector = GitHubConnector()

    print(f"Listando colaboradores reales de {connector.owner}/{connector.repo}...\n")
    accounts = connector.list_active_accounts()

    if not accounts:
        print("No se encontraron colaboradores (o hubo un error - revisa el mensaje de arriba).")
        return

    for acc in accounts:
        print(f"  - {acc['external_account_id']}")

    print("\nEste script es de SOLO LECTURA, no ha revocado nada.")
    print("Para probar una revocación real: python -m scripts.test_github_revoke <username>")


if __name__ == "__main__":
    main()