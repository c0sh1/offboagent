"""
Configuración central de la aplicación.

Usamos pydantic-settings para leer variables de entorno de forma
tipada y validada. Así evitamos "os.getenv" desperdigado por todo
el código y tenemos un único lugar de verdad para la config.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de datos (SQLite para el MVP; en producción sería Postgres)
    database_url: str = "sqlite:///./offboarding.db"

    # Motor de IA (agnóstico de proveedor a nivel de nombres;
    # el proveedor concreto solo se especifica donde se llama a la API)
    llm_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"

    # Entorno
    environment: str = "development"

    # GitHub (opcional; si no se configura, se usa el conector simulado
    # de forma automática -> ver app/connectors/registry.py)
    github_access_token: str = ""
    github_owner: str = ""
    github_repo: str = ""

    # AWS IAM (opcional; si no se configura, se usa el conector simulado)
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"

    # Cuentas de servicio conocidas (las credenciales que usa el propio
    # sistema para conectarse a cada API), separadas por comas. Se
    # excluyen del detector de accesos huérfanos para no generar
    # falsos positivos: no son un riesgo real, son nuestras propias
    # credenciales admin.
    service_account_emails: str = ""

    # Autenticación
    jwt_secret_key: str = "cambia-esto-en-produccion-por-algo-aleatorio-y-largo"
    jwt_expire_hours: int = 24

    # Cifrado de credenciales de conectores (por empresa). Clave Fernet:
    # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    credentials_encryption_key: str = ""


# Instancia única (patrón singleton simple) que se importa en todo el proyecto
settings = Settings()