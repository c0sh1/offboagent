"""
BaseConnector: contrato que TODOS los conectores deben cumplir.

Este es el corazón del patrón Adapter: el resto del sistema (el
servicio de offboarding, el agente) solo conoce esta interfaz.
No le importa si por debajo hay una llamada REST a Slack, un SDK
de AWS, o un mock. Eso permite:

1. Añadir un nuevo sistema sin tocar el código de orquestación.
2. Sustituir un mock por su integración real sin romper nada más
   (mismo contrato, distinta implementación).
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ConnectorResult:
    """Resultado estandarizado de cualquier operación de un conector."""
    success: bool
    detail: str


class BaseConnector(ABC):
    # Debe coincidir con System.connector_key en la base de datos
    connector_key: str

    @abstractmethod
    def revoke_access(self, external_account_id: str) -> ConnectorResult:
        """
        Revoca el acceso de una cuenta en el sistema externo.
        Debe devolver ConnectorResult(success=True/False, detail=...).
        NUNCA debe lanzar una excepción sin capturar: cualquier error
        de la API externa se traduce a success=False + detail con el motivo.
        """
        raise NotImplementedError

    @abstractmethod
    def list_active_accounts(self) -> list[dict]:
        """
        Devuelve todas las cuentas activas en el sistema externo.
        Se usará en la Fase 7 para detectar accesos "huérfanos":
        cuentas que existen en el sistema externo pero que ya no
        deberían estar activas según nuestro grafo de identidad.

        Formato esperado: [{"external_account_id": "...", "email": "..."}, ...]
        """
        raise NotImplementedError