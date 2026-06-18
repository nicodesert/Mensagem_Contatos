"""
Envia mensagens de texto pelo WhatsApp usando a Z-API.
Documentação: https://developer.z-api.io/
"""

from __future__ import annotations

import logging

import requests

from config import settings

logger = logging.getLogger(__name__)

ZAPI_BASE_URL = "https://api.z-api.io"
REQUEST_TIMEOUT_SECONDS = 15


class ZApiError(Exception):
    """Levantada quando a Z-API retorna um erro ou resposta inesperada."""


def _validate_phone(phone: str) -> None:
    """Confere se o telefone só tem dígitos e um tamanho plausível, antes de gastar uma chamada de API com ele."""
    if not phone.isdigit():
        raise ZApiError(f"Telefone inválido (deve conter apenas dígitos): '{phone}'")
    if not (10 <= len(phone) <= 15):
        raise ZApiError(
            f"Telefone com tamanho inesperado ({len(phone)} dígitos): '{phone}'. "
            "Esperado formato DDI+DDD+número, ex: 5511999999999."
        )


def _send_text_url() -> str:
    return (
        f"{ZAPI_BASE_URL}/instances/{settings.zapi_instance_id}"
        f"/token/{settings.zapi_instance_token}/send-text"
    )


def send_text_message(phone: str, message: str) -> dict:
    """
    Envia uma mensagem de texto para um número via Z-API.

    :param phone: número em formato internacional, somente dígitos (ex: 5511999999999)
    :param message: texto já personalizado a ser enviado
    :return: corpo da resposta JSON retornada pela Z-API
    :raises ZApiError: se a requisição falhar, o telefone for inválido, ou a Z-API retornar erro
    """
    _validate_phone(phone)

    payload = {"phone": phone, "message": message}
    headers = {
        "Content-Type": "application/json",
        "Client-Token": settings.zapi_client_token,
    }

    try:
        response = requests.post(
            _send_text_url(),
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise ZApiError(f"Erro de conexão ao chamar a Z-API: {exc}") from exc

    if response.status_code >= 400:
        raise ZApiError(
            f"Z-API retornou status {response.status_code} para o número {phone}: {response.text}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise ZApiError(f"Resposta da Z-API não é um JSON válido: {response.text}") from exc

    logger.debug("Resposta da Z-API para %s: %s", phone, data)
    return data
