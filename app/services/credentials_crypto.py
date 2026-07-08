"""
Cifrado de credenciales de conectores (por empresa).
"""
import json

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings


def _get_fernet() -> Fernet:
    if not settings.credentials_encryption_key:
        raise RuntimeError(
            "Falta CREDENTIALS_ENCRYPTION_KEY en tu .env. Genera una con:\n"
            'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )
    return Fernet(settings.credentials_encryption_key.encode())


def encrypt_credentials(credentials: dict) -> str:
    raw = json.dumps(credentials).encode("utf-8")
    return _get_fernet().encrypt(raw).decode("utf-8")


def decrypt_credentials(encrypted: str) -> dict:
    try:
        raw = _get_fernet().decrypt(encrypted.encode("utf-8"))
    except InvalidToken:
        raise RuntimeError(
            "No se pudieron descifrar las credenciales: la clave CREDENTIALS_ENCRYPTION_KEY "
            "no coincide con la que se usó para cifrarlas."
        )
    return json.loads(raw.decode("utf-8"))