"""
Prueba de revocación REAL en GitHub.

¡CUIDADO! Esto SÍ elimina de verdad a un colaborador del repositorio
configurado en GITHUB_OWNER/GITHUB_REPO. Pide confirmación explícita
antes de ejecutar la acción destructiva - nunca automatices una
acción irreversible sin ese paso, ni siquiera en un script de prueba.

Ejecutar con: python -m scripts.test_github_revoke <username>
"""
import sys

from app.connectors.github_real import GitHubConnector


def main():
    if len(sys.argv) < 2:
        print("Uso: python -m scripts.test_github_revoke <username_a_revocar>")
        return

    username = sys.argv[1]
    connector = GitHubConnector()

    confirm = input(
        f"¿Seguro que quieres eliminar a '{username}' de {connector.owner}/{connector.repo}? "
        f"Escribe 'si' para confirmar: "
    )
    if confirm.strip().lower() != "si":
        print("Cancelado.")
        return

    result = connector.revoke_access(username)
    print("✅ Éxito:" if result.success else "❌ Falló:", result.detail)


if __name__ == "__main__":
    main()