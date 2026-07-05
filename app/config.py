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


# Instancia única (patrón singleton simple) que se importa en todo el proyecto
settings = Settings()