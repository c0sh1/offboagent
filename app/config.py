"""
Configuración central de la aplicación.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./offboarding.db"

    llm_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"

    environment: str = "development"

    # Nota: las credenciales de GitHub/AWS/etc. ya NO viven aquí como
    # variables globales - desde la Fase de multi-tenancy, cada empresa
    # guarda las suyas propias, cifradas, en su propia fila System.

    service_account_emails: str = ""

    jwt_secret_key: str = "cambia-esto-en-produccion-por-algo-aleatorio-y-largo"
    jwt_expire_hours: int = 24

    credentials_encryption_key: str = ""


settings = Settings()