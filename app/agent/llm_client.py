"""
Cliente delgado sobre la API de Anthropic.

Aislamos aquí la ÚNICA parte del proyecto que sabe, explícitamente,
que el proveedor de LLM es Anthropic/Claude. El resto del código
(agent/tools.py, agent/offboarding_agent.py) solo conoce settings.llm_*
de forma genérica. Si algún día cambiaras de proveedor, este es
el único archivo que tocarías.
"""
from anthropic import Anthropic

from app.config import settings

_client: Anthropic | None = None


def get_llm_client() -> Anthropic:
    global _client
    if _client is None:
        if not settings.llm_api_key or "tu-api-key-aqui" in settings.llm_api_key:
            raise RuntimeError(
                "No hay una LLM_API_KEY válida en tu .env. "
                "Consigue una en https://console.anthropic.com/settings/keys "
                "y ponla en la variable LLM_API_KEY."
            )
        _client = Anthropic(api_key=settings.llm_api_key)
    return _client